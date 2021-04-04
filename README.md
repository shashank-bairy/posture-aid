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

## Video Demo

[![PostureAid Demo](https://img.youtube.com/vi/gcaCTre5GGY/0.jpg)](http://www.youtube.com/watch?v=gcaCTre5GGY)

## Tech Stack

- python3.8
- tkinter
- numpy
- opencv
- pytorch

## Working

- Live webcam feed is taken and passes through PoseNet model. More information can be obtained [here](https://www.tensorflow.org/lite/examples/pose_estimation/overview).
- Posenet model returns the coordinates of eyes, nose and ears.
- These coordinates are are used to get the position of the face and establish boundaries for correct posture.
- If the head moves out of the established boundary an alarm sound is played until the head is brought back within the boundary.
- The size of the boundary can be adjusted in the settings menu.

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

## Credits

- The original PoseNet model, weights, code, etc. was created by Google and can be found at [posenet](https://github.com/tensorflow/tfjs-models/tree/master/posenet).

- The port of model was created by Ross Wightman ([@rwightman](https://github.com/rwightman)) is in no way related to Google and it can be found at [posenet-pytorch](https://github.com/rwightman/posenet-pytorch).

- The PostureAid application was created by myself and Sampan S Nayak ([@saoalo](https://github.com/saoalo)) using the port of PoseNet model by Ross Wightman ([@rwightman](https://github.com/rwightman)) present at [posenet-pytorch](https://github.com/rwightman/posenet-pytorch).

## Contributing

All contributions are welcome.
