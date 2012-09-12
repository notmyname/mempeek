import gc
import time

class MemPeek(object):

    def __init__(self, app, conf):
        self.app = app
        self.baseline = self.get_type_counts()[0]
        self.baseline_when = time.gmtime()

    def __call__(self, env, start_response):
        if env['PATH_INFO'] == '/.mempeek':
            show = int(env.get('QUERY_STRING') or 10)
            body = ['MemPeek report at %s\n\n' %
                    time.strftime('%Y-%m-%d %H:%M', time.gmtime())]
            type_counts, requests = self.get_type_counts()

            body.append('Top in current count:\n')
            n = 0
            for k in sorted(type_counts, key=lambda k: type_counts[k],
                            reverse=True):
                body.append('%10d  %s\n' % (type_counts[k], k))
                n += 1
                if n >= show:
                    break

            body.append('\n')

            body.append('Top in growth count since baseline (%s):\n' %
                        time.strftime('%Y-%m-%d %H:%M', self.baseline_when))
            n = 0
            for k in sorted(type_counts,
                    key=lambda k: type_counts[k] - self.baseline.get(k, 0),
                    reverse=True):
                body.append('%10d  %s\n' %
                            (type_counts[k] - self.baseline.get(k, 0), k))
                n += 1
                if n >= show:
                    break

            body.append('\n')

            body.append('Requests currently in memory:\n')
            n = 0
            for req in requests:
                body.append(repr(req))
                body.append('\n')
                for k in sorted(req.environ):
                    body.append('    %20s: %r\n' % (k, req.environ[k]))
                n += 1
                if n >= show:
                    break

            start_response('200 Ok',
                [('Content-Length', str(sum(len(b) for b in body))),
                 ('Content-Type', 'text/plain')])
            return body

        elif env['PATH_INFO'] == '/.mempeek/baseline':
            body = ['MemPeek report at %s\n\nNew baseline recorded.\n' %
                    time.strftime('%Y-%m-%d %H:%M', time.gmtime())]
            self.baseline = self.get_type_counts()[0]
            self.baseline_when = time.gmtime()
            start_response('200 Ok',
                [('Content-Length', str(sum(len(b) for b in body))),
                 ('Content-Type', 'text/plain')])
            return body

        else:
            return self.app(env, start_response)

    def get_type_counts(self):
        type_counts = {}
        gc.collect(2)
        requests = []
        for obj in gc.get_objects():
            t = type(obj)
            n = t.__module__ + '.' + t.__name__
            if n not in type_counts:
                type_counts[n] = 1
            else:
                type_counts[n] += 1
            if n == 'webob.request.Request':
                requests.append(obj)
        return (type_counts, requests)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def make_filter(app):
        return MemPeek(app, conf)

    return make_filter
