Line profiling is the most thorough way to go, but is inappropriate for benchmarking as it adds a huge overhead - [Profiling Python Like a Boss](https://zapier.com/engineering/profiling-python-boss/).

Line profiling seems appropriate for scientific computing. For a web app:
1. find a way to aggregate line profiling for a number of js powered tests while server runs
2. use something like [plop](https://github.com/bdarnell/plop)