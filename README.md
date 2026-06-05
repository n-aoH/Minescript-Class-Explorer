# Minescript-Class-Explorer
A project to explore mienscript classes better in VSCode

# Overview

This project takes advantage of pylance to create interactive documentation of minecraft's classes.

It creates a limited definition of the selected classes to ensure that VSCode will fully access the class definitions. (200k lines -> 5k)

Currently, it is loaded with the full 1.21.11 class list, although I have plans to expand it further.

Example usage below:

<img width="553" height="343" alt="image" src="https://github.com/user-attachments/assets/a25ab453-4a35-4a02-9f05-cf92a20f6595" />

# Usage

:star: This project assumes that you have your 'minescript' folder opened in VScode so that it can search through all the documentation properly.

Download the `vscode.py` file and place it into your minescript directory. Then, ingame, execute:

`\vscode download` - Downloads class list from this github repo
`\vscode auto` - Automatically grabs 6 common classes and compiles them in your minescript documentation

Upon doing this, you will see a `minescript.pyi` file inside of your minescript folder. This is where the classes are stored.

Instead of accessing minescript in your code as:

```py
from system.lib.minescript import *
```

Instead, use:
```py
from minescript import *
```

This allows the .pyi file to be read, while still using the default minescript runtime. (This means that any scripts created using this documentation system will be fully functional to someone without it installed)

To let python know to read the documentation, the following formatting is required:

```py
mc: "net.minecraft.client.Minecraft" = JavaClass("net.minecraft.client.Minecraft").getInstance()
```

This will then let vscode know that every time you reference the mc variable, it should add the intellisence docs from [here](https://mappings.dev/1.21.11/net/minecraft/client/Minecraft.html).

And typing mc.`...` will now have autocomplete!

<img width="506" height="259" alt="image" src="https://github.com/user-attachments/assets/316a18df-4b86-4994-b35f-d2a106dc7dfd" />

Of course, finding the name of these classes can be annoying, so there's also a class finder that works on all currently loaded classes in the documentation.

Just begin typing a class name (the raw thing, not a string) and it will autocomplete.

<img width="655" height="106" alt="image" src="https://github.com/user-attachments/assets/4346f6e7-8fdf-471a-bac3-efc097b8421a" />

You can add a class to the current documentation with `\vscode add <NAME>` and remove it with `\vscode del <NAME>`.

As a reminder, only base 1.21.11 classes are included.
