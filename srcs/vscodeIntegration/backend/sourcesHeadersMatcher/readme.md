# sourcesHeadersMatcher data flow

This folder is organized as a small pipeline:

1. `main.py` traverses the project and aggregates per-file matches.
2. `generateHeader.py` and `protoImplementationMatcher.py` build a normalized map keyed by prototype string.
3. `stringify.py` converts that map into a list of files to write.
4. `render.py` saves those files.
5. `printer.py` prints the planned writes in a readable format.


## 1. `proto`

Built by `resolveProto(startPath, extensions, excludedFolderPath)`.

Shape:

```python
[
    class_proto_list,
    function_proto_list,
    macro_proto_list,
    struct_proto_list,
    typedef_proto_list,
]
```

Example:

```python
[
    [],
    [
        "int compute_total(int base, int extra);",
        "void log_result(int value);",
        "const char *feature_name(void);",
    ],
    [
        "#define FEATURE_NAME \"sourcesHeadersMatcher fixture\"",
    ],
    [
        "struct feature_shadow;",
        "struct feature_toggle {\n    const char *name;\n    int enabled;\n};",
    ],
    [
        "typedef struct runtime_flag {\n    const char *label;\n    int is_active;\n} runtime_flag_t;",
        "typedef runtime_flag_t runtime_flag_alias_t;",
    ],
]
```

Purpose:
- global list of all declarations discovered in the scanned tree
- used as input to `generateHeader(...)`


## 2. Per-file generated header map

Built by:

```python
generateHeader(filePath, proto, source_texts_by_path)
```

Shape:

```python
{
    proto_string: [
        {
            "implementation": implementation_string,
            "source": "/absolute/path/to/file.c",
            "recurence": [
                {
                    "source": "/absolute/path/to/file.c",
                    "times": 2,
                }
            ],
        }
    ]
}
```

Example:

```python
{
    "void log_result(int value);": [
        {
            "implementation": "void log_result(int value)\n{\n    printf(\"result=%d\\n\", value);\n}",
            "source": "/abs/project/services/io/log.c",
            "recurence": [
                {"source": "/abs/project/app/main.c", "times": 1},
                {"source": "/abs/project/services/io/log.c", "times": 1},
            ],
        }
    ],
    "#define FEATURE_NAME \"sourcesHeadersMatcher fixture\"": [
        {
            "implementation": "#define FEATURE_NAME \"sourcesHeadersMatcher fixture\"",
            "source": "/abs/project/config/feature.c",
            "recurence": [
                {"source": "/abs/project/config/feature.c", "times": 1},
                {"source": "/abs/project/app/main.c", "times": 1},
            ],
        }
    ],
}
```

Meaning of fields:
- `proto_string`: declaration that may move to a header
- `implementation`: current concrete text found in a source file
- `source`: source file considered the owner of that declaration
- `recurence`: where the declaration is referenced and how many times


## 3. Aggregated `generatedHeaders`

Built in `main.py` by merging all per-file maps.

Shape:

```python
{
    proto_string: [entry, entry, ...]
}
```

Each list may contain several candidate owner entries for the same proto, coming from different files.

Example:

```python
{
    "int compute_total(int base, int extra);": [
        {
            "implementation": "int compute_total(int base, int extra)\n{\n    return base + extra;\n}",
            "source": "/abs/project/services/math/compute.c",
            "recurence": [
                {"source": "/abs/project/services/math/compute.c", "times": 1},
                {"source": "/abs/project/app/main.c", "times": 1},
            ],
        }
    ]
}
```

This object is the main input of `stringify_headers(generated_headers)`.


## 4. `generatedHeaders` after header assignment

Inside `stringify.py`, `_set_entry_header_paths(generated_headers)` mutates each entry by adding `headerPath`.

Shape:

```python
{
    proto_string: [
        {
            "implementation": "...",
            "source": "/abs/project/services/math/compute.c",
            "recurence": [...],
            "headerPath": "/abs/project/services/math/compute.h",
        }
    ]
}
```

Rules currently used:
- function prototypes go to the header matching each source file
- macro/struct/class/typedef go to the header of the best entry
- "best" means highest recurrence score


## 5. Internal header map

Built by `_build_header_map(generated_headers)`.

Shape:

```python
{
    "/abs/project/services/math/compute.h": [
        "int compute_total(int base, int extra);",
    ],
    "/abs/project/config/feature.h": [
        "const char *feature_name(void);",
        "#define FEATURE_NAME \"sourcesHeadersMatcher fixture\"",
        "struct feature_shadow;",
        "struct feature_toggle {\n    const char *name;\n    int enabled;\n};",
        "typedef struct runtime_flag {\n    const char *label;\n    int is_active;\n} runtime_flag_t;",
        "typedef runtime_flag_t runtime_flag_alias_t;",
    ],
}
```

Purpose:
- groups declarations by destination header file
- this is still an internal structure, not the final render payload


## 6. Internal include map

Built by `_build_source_include_map(generated_headers)`.

Shape:

```python
{
    "/abs/project/app/main.c": {
        "/abs/project/config/feature.h",
        "/abs/project/services/io/log.h",
        "/abs/project/services/math/compute.h",
    },
    "/abs/project/services/math/compute.c": {
        "/abs/project/services/math/compute.h",
    },
}
```

Purpose:
- tells which existing source file should include which generated header
- used to produce updated source file content in memory


## 7. Final stringify payload

Built by `stringify_headers(generated_headers)`.

Shape:

```python
[
    {
        "path": "/abs/project/config/feature.h",
        "string": "#pragma once\n\nconst char *feature_name(void);\n...",
    },
    {
        "path": "/abs/project/app/main.c",
        "string": "#include <stdio.h>\n#include \"../config/feature.h\"\n...",
    },
]
```

This is the key contract between modules.

Meaning:
- `path`: destination file path
- `string`: complete file content to save

Important:
- this payload contains both new header files and rewritten source files
- `stringify.py` is responsible for producing the final file text
- `render.py` should not decide content, only persist it


## 8. Render input/output

Handled by `render_headers(rendered_headers)`.

Input shape:

```python
[
    {"path": "...", "string": "..."},
    {"path": "...", "string": "..."},
]
```

Behavior:
- create parent folders if needed
- write `string` into `path`
- return the same list

`render.py` should stay intentionally dumb.


## 9. Printer input/output

Handled by `format_stringified_headers(stringified_headers)`.

Input shape:

```python
[
    {"path": "...", "string": "..."}
]
```

Output shape:

```python
"Headers (3)\n\n/path/to/a.h\n    #pragma once\n..."
```

Purpose:
- human-readable preview of what would be written
- no filesystem change


## 10. Current `main.py` flow

Current behavior:

```python
traversal_result = traverse_file_system(startPath, excludedFolderPath)
generated_headers = traversal_result["generatedHeaders"]
stringified_headers = stringify_headers(generated_headers)
print(format_stringified_headers(stringified_headers))
```

`traverse_file_system(...)` returns:

```python
{
    "proto": proto,
    "generatedHeaders": generated_headers,
}
```

So the main checkpoints are:
- `proto`: all discovered declarations
- `generatedHeaders`: merged ownership/recurrence map
- `stringified_headers`: final write plan


## Practical rule of thumb

If you want to change:
- matching logic: look at `generateHeader.py` and `protoImplementationMatcher.py`
- header destination selection: look at `_target_headers_for_proto(...)` in `stringify.py`
- source include insertion: look at `_build_source_include_map(...)` and `_string_with_inserted_include(...)`
- filesystem writes: look at `render.py`
- console output: look at `printer.py`
