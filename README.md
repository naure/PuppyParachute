# PuppyParachute

## Goals

### Understand the code

See example runtime values side-by-side with the code.

Annotations can easily be generated from existing unittests
using a nosetests plugin:

    > nosetests3 demo --puppy-package app --puppy-annotate

This will annotate all functions covered by the tests, including example inputs and outputs, for instance:

```python
#? what=that -> Done
def do_things(what):
    print('Doing {}'.format(what))
    return 'Done'
```

This also works for methods with side-effects:

```python
class A(object):
    #? i=2, self=A {n: 10} -> None | self=A {n: 12}
    def inc(self, i):
        self.n += i
```

The #?-annotations can be removed using the deannotate script.

### Understand change

See the effects of a change in all parts of the code.

Inspect changes and accept them by simply copying a file.

Track behavior changes in version control along with code changes.

See an example code change, and the associated change at runtime
in [this commit](https://github.com/naure/PuppyParachute/commit/5532a66eef52b2798fd279748f830ff1f6ab0a79).


### Automatic regression tests

Achieve very high code coverage with few tests and no code change.

Deal with under-tested project, difficult to isolate code, and tough deadlines.


## How it works

* Specify one or more entry-points or test cases to run the code. Entry-points can be more or
  less high-level.

* While running the code, PuppyParachute records every function call, with parameters, relevant environment, behavior, and return values.

* Compare differences in outputs and behavior of the whole code with previous run.

* Check in and track the record as a text/YAML file in version control.
