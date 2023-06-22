# Changes

## 2023-06-18

- refactored to move common code to new repo `message_md` 

## 2022-12-06

- creating github repo and project
- migrated to-dos into github project board

## 2022-12-05

- got reply with quote working so it outputs something like this

```
> > SpongeBob: Calling in sick because I have covid
>
> Mr. Krab: that's the 3rd time in 2 weeks SB!
```

## 2022-12-05

- [x] `video/mp4` attachments not processed - FIXED!
- [x] bug: message with multiple attachment only deals with the first attachment = was using index of array to add items instead of append()  FIXED!

- [x] fix bug with  some attachments not showing up -- was because of a check that was including only messages with `body` so messages with `attachments` were excluded - FIXED!
- [x] include `quotes`

## 2022-12-04

- adding note-to-self folder support
- [x] bug: dies when `daily-notes-folder` is blank in settings
- [x] move images to `media` folder(s) and rename them - bug with  some attachments not showing up

## 2022-12-03

- fixed loading of messages which was missing a whack of messages due to character encoding, set it to `utf-8` on file `open`
- started looking at note-to-self, for some reason my own dated files contain messages to other people #bug

## 2022-12-02

- added messages by date to each persons' and group's folder

## 2022-12-01

- [x] create folders for groups

## 2022-11-30

- Figured out how a message in a Group chat differs from others
- Created `groups.json` and loading for those

## 2022-11-28

- Got sync messages going again
- Added support for logging reactions (optional)

## 2022-11-27

- Added `README.md`  describing the settings file
- Added language support, English for now :

## 2022-11-21

- created `config` folder and renamed `signal-md-config.json` to `people.json`
- created `config\settings.json` with first parameter modified `include-timestamp`

## 2022-11-14

- [Tweeted](https://twitter.com/NoteApps/status/1592253343979667460) about it

> I've been doing something insane: transposing messages and images from @signalapp to #Markdown files, one per day per person ... manually! Before that I had tried using a tool that can decrypt and open a Signal backup file but that wasn't very useful [signal-back](https://github.com/xeals/signal-back)

> A good friend and tech Yoda told me that the bridge he uses for Matrix to Signal uses an #open-source daemon called 'signald'

> So I installed that yesterday on [[Docker]] (on my [[Unraid]] server) and low and behold, it's very useful ... with some additional small shell scripts. This daemon becomes another Signal client device (you need to authorize it like any other device using a QR code and your phone)

> Once it's running you simply run 'signald subscribe' and all of the messages are output to JSON (or another format). The only issue is the images

> BUT for those, not so bad because they are also exported (without file suffixes) with an ID that's inside the JSON for each message containing an attachment. With a bash script, I can move those out of the Docker container to a safe place

> With a Python script (my first ever, shhh!) I am able to read the JSON and convert it to Markdown, adding in YAML front matter like this

> It's only a prototype so far and if the container dies, I'll need to start up the script again but it's a start! Next steps: 
> - [x] Map the phone numbers to names -- that part is hacked
> - [x] Inject timestamps
> - [x] Create separate file per person per day
> - [ ] Put them in my [[Obsidian]] vault
