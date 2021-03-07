## VS linter

Use the `home` key to get to the top.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->

**Table of Contents**

* [Setup](#setup)

<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

## Setup

The formatting tool can be invoked via the Makefile, directly as `tools/format/json_formatter.cgi` (built via `make style-json`), or via cgi at http://dev.narc.ro/cataclysm/format.html

If you're using the Visual Studio solution, you can configure Visual Studio with
commands to format all of the JSON in the project.

1. Build the JsonFormatter project by either building the entire solution or
   just that project. This will create a `tools/format/json_formatter.exe`
   binary.
   
2. Add a new external tool entry ( `Tools` > `External Tools..` > `Add` ) and
   configure it as follows:

   * Title: `Lint All JSON`
   * Command: `C:\windows\system32\windowspowershell\v1.0\powershell.exe`
   * Arguments: `-file $(SolutionDir)\style-json.ps1`
   * Initial Directory: `$(SolutionDir)`
   * Use Output window:

   At this point, you can use the menu ( `Tools` > `Lint All JSON` ) to invoke the
   command and can look in the Output Window for the output of running it.
   Additionally, you can configure a keybinding for this command by navigating to
   `Tools` > `Options` > `Environment` > `Keyboard`, searching for commands
   containing `Tools.ExternalCommand` and pick the one that corresponds to the
   position of your command in the list (e.g. `Tools.ExternalCommand1` if it's the
   top item in the list) and then assign shortcut keys to it.

   

3. If you get errors witch contain `style-json.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at http://go.microsoft.com/fwlink/?LinkID=135170` 

   * change the executionpolicy to `remotesigned` 
   * run `Windows PowerShell` 
   * enter `Set-ExecutionPolicy -Scope CurrentUser` 
   * And enter `remotesigned`

<!-- END doctoc generated TOC please keep comment here to allow auto update -->