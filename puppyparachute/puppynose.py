import logging
import os

from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.puppy')

class PuppyParachute(Plugin):
    name = 'puppy'

    def options(self, parser, env=os.environ):
        super(PuppyParachute, self).options(parser, env=env)

        parser.add_option(
            '--puppy-package', action='append',
            default=env.get('NOSE_PUPPY_PACKAGE'),
            metavar='PACKAGE',
            dest='puppy_packages',
            help='Restrict Puppy traces to selected packages, modules, or classes. '
            'Specify a prefix to match against pkg[.module[:class]]. '
            'If missing, uses --cover-package, or defaults to all packages. '
            '[NOSE_PUPPY_PACKAGE]',
        )

        parser.add_option(
            '--puppy-file', action='store',
            default=env.get('NOSE_PUPPY_FILE', 'puppy_trace.yml'),
            metavar='OUTPUT_FILE',
            help='Write Puppy trace in this file. '
            'The trace is human-readable and can be checked in version control. '
            '[NOSE_PUPPY_FILE or puppy_trace.yml]',
        )

        parser.add_option(
            '--puppy-annotate', action='store_true',
            default=env.get('NOSE_PUPPY_ANNOTATE'),
            help='Annotate source files.'
            'Use puppy-deannotate to remove annotations',
        )

    def configure(self, options, conf):
        super(PuppyParachute, self).configure(options, conf)

        if options.puppy_packages:
            self.enabled = True

        if self.enabled:
            try:
                import puppyparachute
                self.puppyparachute = puppyparachute
                from puppyparachute.tools import tracing
            except ImportError as e:
                log.error('Could not import puppyparachute: {}'.format(e))
                self.enabled = False
                return

            if (
                not options.puppy_packages
                and getattr(options, 'cover_packages', False)
            ):
                options.puppy_packages = options.cover_packages

            if options.puppy_packages:
                log.info('Tracing prefixes: {}'.format(
                    ' '.join(options.puppy_packages)))

            self.tracer = tracing(
                packages=options.puppy_packages,
            )

    def beforeTest(self, test):
        self.tracer.start()

    def afterTest(self, test):
        self.tracer.stop()

    def report(self, stream):

        if self.conf.options.verbosity >= 2:
            stream.write('-' * 70)
            stream.write(
                '\nSaving Puppy trace to {}\n'.format(
                    self.conf.options.puppy_file))

        if self.conf.options.verbosity >= 3:
            stream.write(
                'Traced functions: {}\n'.format(
                    ' '.join(self.tracer.fndb.keys())))

        with open(self.conf.options.puppy_file, 'w') as fd:
            self.tracer.dump(fd)

        if self.conf.options.puppy_annotate:
            if self.conf.options.verbosity >= 2:
                stream.write(
                    'Annotating source files. '
                    'Use puppy-deannotate to remove annotations\n')
            self.puppyparachute.annotate.annotate_all(self.tracer.freeze())
