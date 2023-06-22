This file provides details on how to configure the `signal_md` tool.

Refer to the `message_md\docs` for info on People

## Groups

Add the groups that you are part of in this file:

```
config\groups.json
```

### Fields

- `id` - the unique ID for this group, see **Finding the group ID**
- `slug` - a one-word label for the group, will be used as the folder name
- `person-slug` - a unique one-word label for each person, see **Person**

### Finding the group ID

To find the unique group ID, search through the JSON output from `signald`.

First, send a message to the group in Signal so you can then search for it in the `signald` output.

Once you've sent a message, open the `signald` output and search for `groupV2` and right after that will be the `id` field of the group. This is the value to be placed in the `id` field.

#### Example

Here's a snippet of the output from `signald` with a number of attributes removed for readability sake.

```
{"type":"IncomingMessage",
   "data":{
        "source":{
          "data_message":{
            "groupV2":{
                "id":"G49mXaA6ZEo+EbSCwbU97yYnekOMtQZ8oEhXFDLy9sE=",
```

### Example

Below is an example of the `groups.json` config file with two groups `fishing` and `bikini-bottom`.

```
{
    "groups": [
        {
            "id":"G49mXaA6ZEo+EbSCwbU97yYnekOMtQZ8oEhXFDLy9sE=",
            "slug":"fishing",
            "description":"They get hooked!",
            "people": ["spongebob","patrick"]
        },
        {
            "id":"wPmRPSnq0hajafjtrzecYyod5T1v68hHjvW/ongRcUQ=",
            "slug":"bikini-bottom",
            "description":"Bikini Bottom residents",
            "people": ["spongebob", "mr-krabs", "patrick"]
        }
}
```

