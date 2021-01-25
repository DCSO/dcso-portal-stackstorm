# DCSO Portal StackStorm Package
Copyright (c) 2021, DCSO Deutsche Cyber-Sicherheitsorganisation GmbH

## Install as StackStorm pack

In the st2 command line run
```st2 pack install https://github.com/DCSO/dcso-portal-stackstorm.git```

## Development using Docker

1. Clone this repository and rename it's folder to `dcso_portal`.
2. Clone st2-docker repository: https://github.com/StackStorm/st2-docker.
3. The steps to start StackStorm with docker-compose are described in the st2-docker repository.
  * Make sure to set the path to the folder that contains your packs. Each pack should be in it's own git repository.
    **The pack's folder name has to be equal to the pack name** (in this case `dcso_portal`).
    ``` shell
    export ST2_PACKS_DEV=$HOME/projects/stackstorm-packs
    ```
  * You can also set the port that can be used to access StackStorm.
    ``` shell
    export ST2_EXPOSE_HTTP=0.0.0.0:80
    ```
4. Run docker-compose (within the st2-docker folder) to start or stop StackStorm.
   ``` shell
   docker-compose up -d
   docker-compose down # use this to shut down StackStorm
   ```
5. Enter the st2 command line, register the pack and start the virtual environment.
   ``` shell
   docker-compose exec st2client bash
   st2 run packs.load packs=dcso_portal register=all # register the pack
   st2 run packs.setup_virtualenv packs=dcso_portal  # start the virtual environment
   ```
6. Open your browser and log in using the default credentials: `user: st2admin`, `password: Ch@ngeMe`.
7. Click on `Actions`. You should see a pack called `dcso_portal` in the user interface. You first need to run `set_api_token` with a token you created in DCSO Portal.
8. You can start using and developing the dcso_portal pack now. You can run the following commands using the st2 command line.
* Rerun `st2 run packs.load packs=dcso_portal register=all` if you made changes and want to reload the pack. 
* Run `st2-run-pack-tests -p packs.dev/dcso_portal/` to run the tests.
* Run `docker-compose down --remove-orphans -v` if you want to uninstall the pack and start with a clean installation.

License
-------

[MIT](LICENSE.txt)
