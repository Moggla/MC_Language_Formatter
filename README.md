# What it does

Turn this:
```
#  Comment style 1: formatlist template
// Comment style 2: formatting codes can be found here https://minecraft.gamepedia.com/Formatting_codes

"advMode.mode.auto":                    "Replace"
"advMode.mode.autoexec.bat":            "§fNew         Name"

"advMode.mode.redstone":                "Add In Front 
"advMode.mode.redstoneTriggered":       "§4

"advMode.mode.sequence":                "Add In Front §* Add At Back
"advMode.mode.unconditional":           "---§*---

"entity.minecraft.villager":            "§* Add At Back
"entity.minecraft.villager.armorer":    "§*---
```

into this for all languages:
```json
{
  "advMode.mode.auto":                    "Replace§r",
  "advMode.mode.autoexec.bat":            "§fNew         Name§r",
  "advMode.mode.redstone":                "Add In Front Impulse§r",
  "advMode.mode.redstoneTriggered":       "§4Needs Redstone§r",
  "advMode.mode.sequence":                "Add In Front Chain Add At Back§r",
  "advMode.mode.unconditional":           "---Unconditional---§r",
  "entity.minecraft.villager":            "Villager Add At Back§r",
  "entity.minecraft.villager.armorer":    "Armorer---§r"
}
```

# Create executable
Run
`pyinstaller -F .\MC_Language_Formatter.py --windowe --icon=test.ico`
or [download Windows executable here](/../../releases/latest)
