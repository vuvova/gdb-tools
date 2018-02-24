from distutils.cmd import Command
from distutils.core import setup

class RunTests(Command):
    user_options=[]
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        from subprocess import Popen, PIPE
        from os import getcwd, execlp
        import re
        cwd=getcwd()+'/'+__file__.rstrip('setup.pyc')+'tests'
        stem=cwd+'/test.'
        with open(stem+'gdb', 'r') as fg, open(stem+'in', 'w') as fi, open(stem+'out', 'w') as fo:
            for l in fg:
                if l.startswith('(gdb) '):
                    fi.write(l[6:])
                else:
                    fo.write(l)
        p=Popen(['gdb', '-batch', '-n', '-x', 'test.in'], cwd=cwd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        (o,e)=p.communicate()
        if e: raise Exception(e)
        o = re.sub(r'(=.*) 0x[0-9a-f]+', r'\1 0xXXXXX', o)
        o = re.sub(r'Temporary breakpoint 1 at .*\n', '', o)
        with open(cwd+'/test.reject', 'w') as f: f.write(o)
        execlp('diff', 'diff', '-u', cwd+'/test.out', cwd+'/test.reject')

setup(
    name='gdb-tools',
    packages=['duel', 'pretty_printer'],
    version='1.3',
    description='Various tools to improve the gdb experience',
    license='BSD-3-clause',
    author='Sergei Golubchik',
    author_email='vuvova@gmail.com',
    url='https://github.com/vuvova/gdb-tools',
    keywords=['gdb', 'duel'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Debuggers',
    ],
    package_data={'duel': ['help.md']},
    install_requires=['arpeggio'],
    cmdclass={ 'test': RunTests },
)
