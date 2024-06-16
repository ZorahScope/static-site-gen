# Static Site Generator Project

Welcome to my static site generator project! This is a guided project from [Boot.dev](https://www.boot.dev/) where I dive into building a static site generator from scratch using Python.

## Project Overview

In this project, I follow Boot.dev's high-level, hands-off approach which is more engaging than your typical tutorial. Instead of step-by-step instructions, I'm provided with the names of classes or functions and their expected behaviors. It's up to me to implement and test everything, which makes for a great learning experience.

## How It Works

The main script for the project is main.sh, located in the root folder. Running this script kicks off the process of generating the static site. Here's what it does:

- Recursively Processes Files: The script goes through all the files and subdirectories in the content folder.
- Markdown to HTML: It converts all markdown files in content to HTML files.
- Maintains Structure: The generated HTML files are placed in the public directory, mirroring the structure of the content directory.
- Includes Other Files: Images and other files are also handled appropriately.
- Starts a basic web server that will serve the content from localhost

## Running the Project

To generate your static site, simply execute the main.sh script from the project root directory:

```sh
./main.sh
```

Make sure all your markdown content is in the content directory before running the script.

## Learning Experience

This project was all about taking control of the implementation and debugging process along with putting together my learnings from the previous modules on *Object-Oriented Programming* and *Functional Programming*. It’s a hands-on way to learn and understand how static site generators work under the hood.

This was done during my free time outside of work. From start to finish, it's taken me exactly 3 weeks for a total of 33 hours and 785 lines of code during that period.
It was a great experience where I picked up a lot on how to use my tools more effectively while writing code. The biggest takeaway for me was the extensive practice I've received on writing unittests

Happy coding! If you have any questions or run into issues, feel free to open an issue or reach out.

Enjoy building your static site! 🚀