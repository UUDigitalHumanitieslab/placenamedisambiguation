# `parser.py`

`parser.py` is part of [a pipeline of scripts](../README.md). As it name suggests, it can be used to parse XML and HTML files into plain .txt files that contain the text content from the desired elements. In essence it is a wrapper around [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), allowing for some very basic text extraction options. Under the hood it utilizes BeautifulSoup's HTML parser, making it a very generous (XML) parser that doesn't care about namespaces and allows for HTML entities in the (XML) documents.

## Command line arguments

| Command              | Explanation                                                                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `--help`             | The most basic command, which displays some information on the script's options. Not as detailed as this README.                                |
| `--dir`              | The root directory that your input files are in. Note that the script will look for files in all subfolders as well.                            |
| `--ext`              | The extension of the files to be included. Defaults to '.xml'                                                                                   |
| `--out`              | The directory where to write the output. Has to exist, i.e. will not be created. The script will not start as long as the folder doesn't exist. |
| `--route_to_content` | The most interesting and complex option for this script. More details below                                                                     |


## `--route_to_content`

The route (i.e. path) to the node the textual content needs to be extracted from. The format of this route should be as follows: `tagname#tagname` or `tagname#tagname[attribute]`. Note that single tags are also allowed (e.g. `tagname[attribute]` will work).

### Examples

Given this XML:

```xml
<parent>
    <content>Text</content>
</parent>
```

You can extract the text by supplying the following argument to the script: `--route_to_content parent#content`


This would also work if they are multiple childnodes in parent:

```xml
<parent>
    <content>Text</content>
    <content>Text</content>
    <content>Text</content>
</parent>
```

In this case, the textual content will be extracted and joined (with a space in between). Issueing the `--route_to_content parent#content` argument would result in the following output: 'Text Text Text'.

Note that it is also allowed to leave `parent` out of the route in above examples, simply supplying `content` would also work.

#### more complex XML structures

If your XML is a bit more complex than the examples above, you need to be very precise with the path (a.k.a. route) you offer. Consider for example this XML:

```xml
<parent>
    <child>
        <grandchild>
            <content>Text</content>
        </grandchild>
    </child>
</parent>
```

If you now provide `child#content`, the script won't find anything. You should either do `child#grandchild#content`, `grandchild#content`, or even `content`. However, the last option has it's own cautions:

```xml
<parent>
    <child>
        <grandchild>
            <content>Text</content>
        </grandchild>
    </child>
    <anotherchild>
        <grandchild>
            <content>Text2</content>
        </grandchild>
    </anotherchild>
</parent>
```

If you now provide `content`, both texts will be found, resulting in the output 'Text Text2'. If you need either one but not both, be precise in the route you supply to the script.

#### attributes

But what if the content is in an element's attribute? For example:

```xml
<parent>
    <child content='Text'></child>
</parent>
```

Provide the following route: `child[content]`. This also works if multiple child nodes with content attribute exist. Given

```xml
<parent>
    <child content='Text'></child>
    <child content='Text2'></child>
    <child content='Text3'></child>
</parent>
```

The output of `child[content]` will be `Text Text2 Text3'.

#### Wildcard (`*`)

Consider the following XML:

```xml
<parent>
    <child>
        <sibling1>
            <content>Text</content>
        </sibling1>
        <sibling2>
            <content>Text</content>
        </sibling2>
    </child>
</parent>
```

To extract the content here, you could use a wildcard:
`child#*#content`.


#### Valid routes

- do not contain empty elements (i.e. `##` is not allowed)
- has an attribute only in the last element (i.e. `child[attribute]#grandchild` is not allowed)
