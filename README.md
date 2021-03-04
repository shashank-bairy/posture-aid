# PostureAid

Application used to aid computer users to maintain good posture.

It uses live camera feed to check if the position of your head is within the defined boundary. If your head is outside the boundary, then warning sound is played. The sound is stopped only after your head is brought inside the boundary.

## Instructions for use

1. Launch the application. You should be able to see the live camera feed.

2. Sit upright and position you head in proper posture. Press the Start button to start the monitoring function.

3. On pressing the Start button, the boundary position set to the boundary position at that instant. Now, the boundary stops moving.

4. If your head moves outside the boundary, warning sound is played and it won't stop until you bring your head within the boundary.

5. Height and width of the boundary can be increased/decreased in the Settings menu.

6. The monitoring can be stopped by pressing the Stop option.

## Tech Stack

- python
- tkinter
- numpy
- opencv

## Setting up locally

1. Create a python virtual environment and activate it.

   `python3 -m venv env`

   `source env/bin/activate`

2. Install tkinter if not yet installed.

3. Clone the repository and navigate inside `posture-aid` folder.

4. Install required python packages.

   `pip3 install -r requirements.txt`

5. Launch the application

   `python3 app.py`

## Contributing

All contributions are welcome.
