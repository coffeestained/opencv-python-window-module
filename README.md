# opencv-python-window-module

In-progress refactoring of previous OpenCV experiments. The core module creates an overlay on the screen to visualize actions and workflow outputs. A service class continuously captures the screen or a selected window, providing both the current and previous frame.

Using the UI, you can provide a path to a `.zip` file that defines a workflow. This archive must contain a `manifest.json` and any required assets. See the **Workflow ZIP Package Specification** section below for more details.

Once the workflow is running, the terminal will log the operation outputs, and the screen overlay will visually reflect the current state of the operations.

---

## System Requirements

```bash
sudo apt-get update
sudo apt install python3.6
sudo apt install xdotool
sudo apt install libgirepository1.0-dev libcairo2-dev python3-gi python3-gi-cairo
sudo apt install python3-tk python3-dev
sudo apt install wmctrl
sudo apt install imagemagick x11-utils x11-xserver-utils xdotool
sudo apt install ffmpeg -y
```

---

## Getting Started

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## Workflow ZIP Package Specification

The Workflow ZIP file defines a self-contained computer vision pipeline for object detection and tracking. It **must** include a `manifest.json` and any image or data assets required for the defined operations.

>  **Note**: All assets declared in the `manifest.json` must be present inside the ZIP file. The workflow archive must be completely self-contained.

### ✅ Currently Supported Operations

- `track_keypoints`: A basic keypoint-based tracking operation.  
  It will detect an object from a reference image, generate keypoints, and attempt to track those keypoints frame-to-frame.  
  If the object is lost, the system will fall back to detection mode and resume tracking once reacquired.

---

###  Required ZIP Structure

```
workflow_package.zip
├── manifest.json         # Main manifest describing the workflow steps
├── assets/               # Required: Directory for reference images or supporting files
│   └── target.jpg
└── config/               # Optional: Custom parameters or metadata
    └── params.yaml
```

---

###  Example `manifest.json`

```json
{
  "workflow_name": "object_tracking_demo",
  "steps": [
    {
      "id": "track_object",
      "operation": "track_keypoints",
      "inputs": ["assets/target.jpg"],
      "outputs": ["tracked_object"],
      "params": {
        "threshold": 0.75
      },
      "run_once": false
    }
  ]
}
```

---

###  Field Descriptions

| Field             | Type       | Required | Description                                                  |
|------------------|------------|----------|--------------------------------------------------------------|
| `workflow_name`  | string     | ✅       | A name for the workflow                                      |
| `steps`          | array      | ✅       | List of operations to perform                                |
| `steps[].id`     | string     | ✅       | Unique ID for the step                                       |
| `steps[].operation` | string  | ✅       | Name of the registered operation (`track_keypoints`, etc.)   |
| `steps[].inputs` | array      | ✅       | Input asset paths or context keys                            |
| `steps[].outputs`| array      | ✅       | Context keys to store output under                           |
| `steps[].params` | object     | ❌       | Operation-specific parameters                                |
| `steps[].run_once` | bool     | ❌       | If true, this step runs only once before the main frame loop |

---

###  Validation Rules

- The ZIP **must** contain `manifest.json` at the root.
- All asset files referenced in the manifest **must exist** inside the ZIP.
- The manifest must define at least one valid `step` with a supported `operation`.

---
