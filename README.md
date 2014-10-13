# PuppyParachute

## Goals

### Understand the code
    
See example runtime values side-by-side with the code.

Annotations can easily be generated from existing unittests
using a nosetests plugin:

    > nosetests3 demo --puppy-package app

This will annotate all functions covered by the tests, including inputs and outputs, for instance:

```python
#? what=that -> Done
def do_things(what):
    print('Doing {}'.format(what))
    return 'Done'
```

The #?-annotations can be removed using the deannotate script.

### Understand change

See the effects of a change in all parts of the code.

Inspect changes and accept them by simply copying a file.

Track behavior changes in version control along with code changes.

See an example code change, and the associated change at runtime
in [this commit](commit/5532a66eef52b2798fd279748f830ff1f6ab0a79).


### Automatic regression tests

Achieve very high code coverage with few tests and no code change.

Deal with under-tested project, difficult to isolate code, and tough deadlines.


## How it works

* Specify one or more entry-points to run the code. Entry-points can be more or
  less high-level.

* Run the code and record every function call, with parameters, relevant environment, behavior, and return value.

* Compare differences in outputs and behavior of the whole code with previous run.

* Check in the new record as a text file.
