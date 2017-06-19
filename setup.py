from distutils.core import setup
setup(
    name='gdb-tools',
    packages=['duel', 'pretty_printer'],
    version='1.0',
    description='Tools for gdb',
    license='BSD-3-clause',
    author='Sergei Golubchik',
    author_email='vuvova@gmail.com',
    url='https://github.com/vuvova/gdb-tools',
    keywords=['gdb', 'duel'],
    package_data={'duel': ['help.md']},
    install_requires=['arpeggio'],
)
