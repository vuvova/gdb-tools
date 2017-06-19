from distutils.core import setup
setup(
    name='duel',
    packages=['duel', 'gdb_pretty'],
    version='1',
    description='Tools for gdb',
    license='BSD 3-clause "New" or "Revised" License',
    author='Sergei Golubchik',
    author_email='sergii@pisem.net',
    url='https://github.com/vuvova/gdb-tools',
    keywords=['gdb', 'duel'],
    classifiers=[],
	package_data={'': ['help.md']},
	install_requires=['arpeggio'],
)
