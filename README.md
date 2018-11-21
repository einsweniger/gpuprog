## (Optional) create a virtualenv

you can do this if you do not want to install the dependencies globally

### create venv

    python -m venv venv

### activate venv

You will have to do this every time you exit your shell.
To exit the sandbox, run `decativate`.

#### lunix shell 

    source ./venv/bin/activate

#### windows 

##### cmd.exe

    .\venv\Scripts\activate

##### powershell

as **admin**, execute:

    Set-ExecutionPolicy RemoteSigned
    
to allow execution of signed remotely scripts.
After that, you'll be able to execute as **regular user**:

    .\venv\Scripts\activate

(for details, see: https://virtualenv.pypa.io/en/stable/userguide/#activate-script)


## install requirements

    pip install -r requirements.txt


## review configuration

check config.py for settings and change to your preferences.

## run program

    python -m ex4.ex4

You can reload your edited shaders by pressing [R] on your Keyboard.
You don't have to restart the program.