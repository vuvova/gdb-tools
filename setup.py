from distutils.core import setup
setup(
    name='gdb-tools',
    packages=['duel', 'pretty_printer'],
    version='1.0',
    description='Various tools to improve the gdb experience',
    license='BSD-3-clause',
    author='Sergei Golubchik',
    author_email='vuvova@gmail.com',
    url='https://github.com/vuvova/gdb-tools',
    keywords=['gdb', 'duel'],
    classifiers=[
        'Development Status :: 3 - Alpha',
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
)
