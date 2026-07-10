# ROS2 기반 UGV 자율주행 및 공장 안전 감지 시스템

## 1. 프로젝트 개요

본 프로젝트는 **ROS2 기반 UGV(Unmanned Ground Vehicle)** 를 활용하여 공장 내부를 자율주행하며, 위험 상황을 감지하고 관리자에게 전달하는 것을 목표로 진행한 졸업 프로젝트이다.

UGV는 LiDAR 기반 SLAM 및 Navigation을 통해 실내 환경을 주행하고, 카메라와 YOLO 모델을 활용하여 공장 내 안전 이상 상황을 인식한다. 또한 IMU 센서를 추가하여 고속 회전 및 주행 상황에서 발생하는 위치 추정 오차를 줄이고, ROS2 bag 데이터를 이용해 주행 성능과 센서 데이터를 비교 분석하였다.

---

## 2. 프로젝트 목표

* ROS2 기반 UGV 자율주행 시스템 구축
* LiDAR 기반 SLAM 및 Navigation 구현
* IMU 센서 적용을 통한 위치 추정 안정성 개선
* YOLO 기반 공장 안전 상황 감지 기능 구현
* 카메라 기반 객체/자세 인식 노드 연동
* 주행 속도 향상을 위한 Navigation 파라미터 튜닝
* ROS2 bag 데이터를 활용한 주행 결과 비교 및 분석
* 고속 주행/회전 시 발생하는 SLAM 및 Localization 오차 원인 분석

---

## 3. 개발 환경

| 구분             | 내용                                                              |
| -------------- | --------------------------------------------------------------- |
| OS             | Ubuntu Linux                                                    |
| ROS            | ROS2 Humble                                                     |
| Robot Platform | UGV / TurtleBot 계열 ROS2 기반 이동 로봇                                |
| SLAM           | slam_toolbox                                                    |
| Navigation     | Nav2                                                            |
| Localization   | AMCL                                                            |
| Sensor Fusion  | robot_localization EKF                                          |
| LiDAR          | RPLidar / SLidar                                                |
| IMU            | `/imu/data` topic 기반 IMU                                        |
| Camera         | USB Camera / v4l2_camera                                        |
| AI Model       | YOLOv11 Pose, YOLO Smoke Detection                              |
| Language       | Python, C++, YAML, Launch Python                                |
| Tools          | RViz2, rqt_image_view, ros2 bag, OpenCV, cv_bridge, Ultralytics |

---

## 4. 전체 시스템 구조

```text
UGV Robot
├── Sensor Layer
│   ├── LiDAR
│   │   └── /scan
│   ├── IMU
│   │   └── /imu/data
│   └── Camera
│       └── /v4l2_camera/image_raw
│
├── Localization / Mapping Layer
│   ├── slam_toolbox
│   ├── AMCL
│   └── robot_localization EKF
│       └── /odom/filtered
│
├── Navigation Layer
│   ├── Nav2
│   ├── controller_server
│   ├── planner_server
│   ├── local_costmap
│   └── global_costmap
│
├── Perception Layer
│   ├── YOLOv11 Pose Detection
│   └── YOLO Smoke Detection
│
└── Application Layer
    ├── 위험 상황 판단
    ├── 관리자 알림
    └── 주행 데이터 기록 및 분석
```

---

## 5. 주요 ROS2 노드 구성

| 노드                              | 역할                          |
| ------------------------------- | --------------------------- |
| `sllidar_node` / `rplidar_node` | LiDAR scan 데이터 발행           |
| `v4l2_camera_node`              | USB 카메라 이미지 토픽 발행           |
| `imu_node`                      | IMU 센서 데이터 발행               |
| `ekf_filter_node`               | odometry와 IMU 데이터 융합        |
| `slam_toolbox`                  | 실내 지도 작성                    |
| `amcl`                          | 지도 기반 위치 추정                 |
| `controller_server`             | 로봇 주행 제어                    |
| `planner_server`                | 경로 계획                       |
| `bt_navigator`                  | Navigation behavior tree 실행 |
| `yolo_pose_node`                | YOLOv11 기반 사람 자세 인식         |
| `smoke_detection_node`          | 연기 감지                       |
| `alert_node`                    | 위험 상황 관리자 전달                |

---

## 6. 주요 토픽

| Topic                    | 설명                     |
| ------------------------ | ---------------------- |
| `/scan`                  | LiDAR LaserScan 데이터    |
| `/imu/data`              | IMU 센서 데이터             |
| `/odom`                  | 기본 odometry            |
| `/odom/filtered`         | EKF로 보정된 odometry      |
| `/tf`                    | 좌표계 변환 정보              |
| `/tf_static`             | 정적 좌표계 변환 정보           |
| `/cmd_vel`               | 로봇 속도 명령               |
| `/map`                   | SLAM 또는 저장된 지도         |
| `/amcl_pose`             | AMCL 기반 현재 위치          |
| `/v4l2_camera/image_raw` | 카메라 원본 이미지             |
| `/yolo/pose`             | YOLO pose detection 결과 |
| `/yolo/smoke`            | 연기 감지 결과               |

---

## 7. TF 구조

프로젝트에서 사용한 기본 TF 구조는 다음과 같다.

```text
map
└── odom
    └── base_link
        ├── laser_frame
        ├── imu_link
        └── camera_link
```

각 프레임의 역할은 다음과 같다.

| Frame         | 설명                    |
| ------------- | --------------------- |
| `map`         | 전역 지도 좌표계             |
| `odom`        | 로봇의 연속적인 odometry 좌표계 |
| `base_link`   | 로봇 본체 기준 좌표계          |
| `laser_frame` | LiDAR 기준 좌표계          |
| `imu_link`    | IMU 기준 좌표계            |
| `camera_link` | 카메라 기준 좌표계            |

프로젝트 중 `map -> odom`, `odom -> base_link` 방향을 혼동하여 TF 오류가 발생했으며, 최종적으로는 ROS Navigation 표준 구조에 맞게 정리하였다.

---

## 8. 구현 내용

### 8.1 LiDAR 기반 SLAM

LiDAR에서 발행되는 `/scan` 데이터를 이용하여 `slam_toolbox`로 실내 지도를 작성하였다.

구현 내용은 다음과 같다.

* LiDAR launch 파일 수정
* LiDAR serial port 설정
* `frame_id` 설정
* scan mode 설정
* angle compensation 적용
* SLAM Toolbox를 이용한 mapping 수행
* RViz2에서 map 생성 결과 확인
* 고속 회전 시 map이 틀어지는 문제 분석

---

### 8.2 Navigation 구현

Nav2를 이용하여 로봇의 목표 지점 이동을 구현하였다.

구현 내용은 다음과 같다.

* Nav2 bringup 실행
* AMCL 기반 localization 적용
* global planner 설정
* local controller 설정
* costmap layer 설정
* keyboard teleop 및 goal navigation 테스트
* 속도 증가에 따른 주행 안정성 확인
* 장애물 주변 cost 반응 속도 확인

---

### 8.3 IMU 적용

고속 회전 및 주행 시 odometry만 사용할 경우 SLAM과 localization 오차가 커지는 문제가 발생하였다. 이를 개선하기 위해 IMU 센서를 추가하고 EKF에 연결하였다.

구현 내용은 다음과 같다.

* IMU node 실행 확인
* `/imu/data` topic echo 확인
* EKF parameter에 IMU topic 추가
* yaw 및 yaw rate 중심으로 IMU 데이터 사용
* 2D 이동 로봇 특성에 맞게 roll/pitch 정보는 제한적으로 사용
* `/odom/filtered` topic 확인
* IMU 적용 전후 bag 데이터 비교

---

### 8.4 EKF 기반 센서 융합

`robot_localization` 패키지의 `ekf_filter_node`를 사용하여 odometry와 IMU 데이터를 융합하였다.

주요 설정 방향은 다음과 같다.

```yaml
ekf_filter_node:
  ros__parameters:
    frequency: 30.0
    sensor_timeout: 0.1
    two_d_mode: true

    map_frame: map
    odom_frame: odom
    base_link_frame: base_link
    world_frame: odom

    imu0: /imu/data
```

IMU 설정에서는 2D 로봇 주행에 필요한 yaw 방향 정보를 중심으로 사용하였다.

```yaml
imu0_config:
  [
    false, false, false,
    false, false, true,
    false, false, false,
    false, false, true,
    false, false, false
  ]
```

이를 통해 로봇 회전 시 발생하는 방향 추정 오차를 줄이고자 하였다.

---

### 8.5 YOLOv11 Pose Detection

카메라 영상에서 사람의 자세를 인식하기 위해 YOLOv11 Pose 모델을 ROS2 노드로 연동하였다.

구현 내용은 다음과 같다.

* USB camera 실행
* `/v4l2_camera/image_raw` topic 구독
* OpenCV와 cv_bridge를 이용한 이미지 변환
* Ultralytics YOLOv11 Pose 모델 적용
* Pose detection 결과 시각화
* frame 단위 detection 안정화를 위한 filtering 적용
* CPU fallback 환경에서 실행 가능하도록 수정

Pose detection 안정화를 위해 다음과 같은 구조를 적용하였다.

```text
Camera Image
→ cv_bridge
→ OpenCV Image
→ YOLOv11 Pose Inference
→ Pose Filtering
→ Detection Result Publish
```

---

### 8.6 Smoke Detection

공장 내 화재 위험 상황을 감지하기 위해 연기 감지 모델을 적용하였다.

구현 내용은 다음과 같다.

* 연기 감지용 YOLO 모델 적용
* 카메라 이미지 입력 처리
* smoke class detection
* 위험 상황 발생 시 관리자 전달 구조 설계
* ROS2 topic 기반 detection result publish

---

### 8.7 관리자 알림 구조

YOLO 기반 perception node에서 감지한 결과를 기반으로 위험 상황을 판단하고, 관리자에게 전달하는 구조를 설계하였다.

예상 흐름은 다음과 같다.

```text
YOLO Detection Result
→ 위험 상황 판단
→ alert topic publish
→ 관리자 시스템 전달
```

---

## 9. 코드 수정 사항 정리

### 9.1 LiDAR Launch 파일 수정

LiDAR 실행을 위해 launch 파일에서 다음 항목을 수정하였다.

```python
channel_type = LaunchConfiguration('channel_type', default='serial')
serial_port = LaunchConfiguration(
    'serial_port',
    default='/dev/serial/by-path/platform-3610000.usb-usb-0:2.1:1.0-port0'
)
serial_baudrate = LaunchConfiguration('serial_baudrate', default='115200')
frame_id = LaunchConfiguration('frame_id', default='laser_frame')
inverted = LaunchConfiguration('inverted', default='false')
angle_compensate = LaunchConfiguration('angle_compensate', default='true')
scan_mode = LaunchConfiguration('scan_mode', default='Sensitivity')
```

수정 목적은 다음과 같다.

* USB 포트 번호가 바뀌어도 LiDAR를 안정적으로 인식하기 위함
* `/dev/ttyUSB0`, `/dev/ttyUSB1`처럼 변동 가능한 포트 대신 `/dev/serial/by-path` 사용
* LiDAR frame을 `laser_frame`으로 통일
* scan 품질 향상을 위해 angle compensation 활성화

---

### 9.2 Navigation Parameter 수정

속도 향상과 주행 안정성을 위해 Navigation 관련 yaml 파일을 수정하였다.

주요 수정 대상은 다음과 같다.

```yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0
```

```yaml
FollowPath:
  max_vel_x
  min_vel_x
  max_vel_theta
  acc_lim_x
  acc_lim_theta
  decel_lim_x
  decel_lim_theta
```

수정 목적은 다음과 같다.

* 로봇 최고 속도 증가
* 회전 속도 조정
* 가속/감속 제한 조정
* keyboard teleop 및 goal navigation 반응성 개선
* 고속 주행 시 경로 이탈 최소화

---

### 9.3 Costmap Parameter 수정

장애물 반응 속도와 회피 성능을 개선하기 위해 costmap 설정을 수정하였다.

수정 대상은 다음과 같다.

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency
      publish_frequency
      inflation_radius
      obstacle_layer
      inflation_layer
```

```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency
      publish_frequency
      inflation_radius
      obstacle_layer
      static_layer
```

수정 목적은 다음과 같다.

* 장애물 주변 cost 반응 속도 개선
* inflation 영역 조정
* 로봇 주변 장애물 감지 반응 개선
* 속도 증가 후 장애물 회피 안정성 확보

---

### 9.4 AMCL Parameter 수정

Localization 안정성을 위해 AMCL parameter를 수정하였다.

수정한 주요 항목은 다음과 같다.

```yaml
amcl:
  ros__parameters:
    min_particles
    max_particles
    max_beams
    alpha1
    alpha2
    alpha3
    alpha4
    alpha5
    update_min_d
    update_min_a
    laser_model_type
```

수정 목적은 다음과 같다.

* 회전 시 localization 흔들림 감소
* LiDAR scan matching 안정성 향상
* particle filter 기반 위치 추정 정확도 개선
* 고속 주행 시 위치 추정 지연 완화

---

### 9.5 EKF Parameter 수정

IMU 데이터를 적용하기 위해 EKF yaml 파일을 수정하였다.

```yaml
ekf_filter_node:
  ros__parameters:
    use_sim_time: false
    frequency: 30.0
    sensor_timeout: 0.1
    two_d_mode: true

    map_frame: map
    odom_frame: odom
    base_link_frame: base_link
    world_frame: odom

    imu0: /imu/data
```

IMU config는 yaw 및 yaw angular velocity를 중심으로 설정하였다.

```yaml
imu0_config:
  [
    false, false, false,
    false, false, true,
    false, false, false,
    false, false, true,
    false, false, false
  ]
```

수정 목적은 다음과 같다.

* IMU yaw 정보를 localization에 반영
* 고속 회전 시 odometry drift 보완
* `/odom/filtered` 기반 주행 안정성 개선
* 2D 로봇 주행 환경에 맞게 불필요한 축 제거

---

### 9.6 YOLOv11 Pose Node 수정

카메라 topic과 YOLO node 연결을 위해 Python 코드를 수정하였다.

주요 수정 방향은 다음과 같다.

```python
self.subscription = self.create_subscription(
    Image,
    '/v4l2_camera/image_raw',
    self.image_callback,
    10
)
```

수정 내용은 다음과 같다.

* camera topic 이름 확인 후 subscription topic 수정
* cv_bridge를 이용해 ROS Image를 OpenCV 이미지로 변환
* YOLOv11 Pose 모델 로드
* inference 결과 시각화
* detection 결과 publish
* pose 결과 안정화를 위한 filtering 추가

---

### 9.7 Camera Node 수정 및 확인

카메라가 정상적으로 실행되지 않는 문제가 있어 camera node와 topic을 확인하였다.

확인 명령어는 다음과 같다.

```bash
ros2 topic list
ros2 topic echo /v4l2_camera/image_raw
rqt_image_view
```

`rqt_image_view`가 없을 경우 다음과 같이 설치할 수 있다.

```bash
sudo apt install ros-humble-rqt-image-view
```

---

### 9.8 Source 및 Build 문제 수정

패키지를 찾지 못하거나 node가 실행되지 않는 문제가 발생하여 workspace build와 source 설정을 확인하였다.

```bash
colcon build
source install/setup.bash
```

bashrc 내부 확인 명령어는 다음과 같다.

```bash
cat ~/.bashrc
```

bashrc에 source를 추가하는 예시는 다음과 같다.

```bash
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 10. 오류 및 해결 사항

### 10.1 `/imu/data` Topic이 안 들어오는 문제

#### 증상

```bash
ros2 topic echo /imu/data
```

명령어를 실행해도 IMU 데이터가 출력되지 않았다.

#### 원인

* IMU node가 launch에 포함되지 않음
* IMU sensor가 정상적으로 연결되지 않음
* USB serial port가 변경됨
* launch 반복 실행 중 장치 번호가 바뀜

#### 해결

* IMU node 실행 여부 확인
* `ros2 node list`로 node 확인
* `/dev/ttyUSB*` 확인
* `/dev/serial/by-path` 사용 검토
* launch 파일에 IMU node 포함 여부 확인

---

### 10.2 USB Serial Port 변경 문제

#### 증상

LiDAR 또는 IMU가 `/dev/ttyUSB0`에서 `/dev/ttyUSB2` 등으로 바뀌면서 실행되지 않았다.

#### 원인

Linux에서 USB 장치 연결 순서에 따라 device name이 변경됨.

#### 해결

`/dev/ttyUSB0` 대신 `/dev/serial/by-path` 경로를 사용하였다.

예시:

```python
serial_port = LaunchConfiguration(
    'serial_port',
    default='/dev/serial/by-path/platform-3610000.usb-usb-0:2.1:1.0-port0'
)
```

이를 통해 장치 번호 변경으로 인한 실행 오류를 줄였다.

---

### 10.3 `package not found` 오류

#### 증상

```bash
Package '패키지명' not found
```

#### 원인

* workspace build가 되지 않음
* `install/setup.bash`를 source하지 않음
* 패키지 이름이 잘못됨
* 현재 terminal에 ROS 환경이 적용되지 않음

#### 해결

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 pkg list | grep 패키지명
```

---

### 10.4 `node not found` 오류

#### 증상

launch 실행 시 특정 node를 찾을 수 없다는 오류 발생.

#### 원인

* 실행 파일 이름 오류
* `setup.py` 또는 `CMakeLists.txt` 설정 누락
* colcon build 미실행
* source 미적용

#### 해결

```bash
colcon build --packages-select 패키지명
source install/setup.bash
ros2 run 패키지명 실행파일명
```

---

### 10.5 YOLO Subscription Count가 0인 문제

#### 증상

YOLO node는 실행되지만 image topic을 구독하지 못함.

#### 원인

* camera topic 이름이 코드와 다름
* camera node가 실행되지 않음
* YOLO node가 잘못된 topic을 subscribe함
* QoS 설정 차이 가능성

#### 해결

현재 camera topic 확인:

```bash
ros2 topic list
```

카메라 topic echo 확인:

```bash
ros2 topic echo /v4l2_camera/image_raw
```

YOLO node의 subscription topic을 실제 camera topic에 맞게 수정하였다.

---

### 10.6 Camera 화면이 안 뜨는 문제

#### 증상

카메라 node를 실행해도 영상이 보이지 않음.

#### 원인

* camera device 번호 오류
* v4l2 camera 설정 오류
* topic 이름 불일치
* rqt_image_view 미설치

#### 해결

```bash
ros2 run v4l2_camera v4l2_camera_node
```

이미지 확인:

```bash
rqt_image_view
```

device 확인:

```bash
ls /dev/video*
```

---

### 10.7 Costmap Warning

#### 증상

Navigation 중 costmap warning 발생.

#### 원인

* TF delay
* sensor data timeout
* LiDAR scan topic 지연
* costmap update frequency 문제
* obstacle layer 설정 문제

#### 해결

* TF tree 확인
* `/scan` topic 정상 출력 확인
* costmap update/publish frequency 조정
* robot footprint 및 inflation radius 확인
* obstacle layer 설정 재검토

---

### 10.8 Message Dropping 문제

#### 증상

ROS2 message가 제대로 처리되지 않고 dropping 발생.

#### 원인

* sensor publish rate가 높음
* 로봇 PC의 처리 성능 부족
* YOLO inference 부하
* QoS queue size 부족
* topic 처리 속도보다 입력 속도가 빠름

#### 해결

* camera frame rate 조정
* YOLO 모델 경량화
* queue size 조정
* 필요 없는 topic publish 줄이기
* CPU fallback 환경에서 inference 속도 확인

---

### 10.9 SLAM Map이 깨지는 문제

#### 증상

로봇을 고속으로 회전시키면 map이 찌그러지거나 틀어짐.

#### 원인

* 고속 회전 시 odometry drift 증가
* IMU 미사용으로 yaw 추정 불안정
* LiDAR scan matching이 회전 속도를 따라가지 못함
* TF delay 발생 가능성

#### 해결

* 속도 제한 조정
* IMU 추가
* EKF 적용
* AMCL parameter 수정
* bag data로 IMU 적용 전후 비교

---

### 10.10 Navigation 반응이 느려지는 문제

#### 증상

파라미터 수정 후 keyboard 입력이나 navigation 반응이 느려짐.

#### 원인

* controller frequency가 낮음
* acceleration limit이 너무 낮음
* costmap update가 느림
* obstacle inflation이 과하게 설정됨

#### 해결

* controller frequency 확인
* acceleration parameter 재조정
* local costmap update frequency 조정
* inflation radius를 과하게 키우지 않도록 조정

---

## 11. ROS2 Bag 데이터 분석

프로젝트에서는 주행 데이터 비교를 위해 ROS2 bag을 기록하고 재생하였다.

### 11.1 Bag Record

```bash
ros2 bag record /scan /tf /tf_static /odom /odom/filtered /imu/data /cmd_vel
```

필요한 경우 전체 topic을 기록할 수 있다.

```bash
ros2 bag record -a
```

---

### 11.2 Bag Play

```bash
ros2 bag play bag파일명
```

예시:

```bash
ros2 bag play imu_compare_bag_0.db3
```

---

### 11.3 분석 목적

bag 데이터를 이용해 다음 항목을 비교하였다.

* IMU 적용 전후 yaw 변화
* odometry drift
* `/odom`과 `/odom/filtered` 차이
* 고속 회전 시 localization 안정성
* SLAM map 품질
* 속도 증가 전후 주행 안정성
* RMSE/RPE 기반 위치 오차

---

## 12. 성능 개선 방향

프로젝트 진행 중 다음과 같은 개선을 수행하였다.

### 12.1 주행 속도 개선

기본 저속 주행 상태에서 Navigation parameter를 조정하여 목표 속도를 단계적으로 높였다.

수정한 항목은 다음과 같다.

* `max_vel_x`
* `max_vel_theta`
* `acc_lim_x`
* `acc_lim_theta`
* `decel_lim_x`
* `decel_lim_theta`
* controller frequency
* local costmap update frequency

속도 증가 후에는 장애물 회피, costmap 반응, localization 안정성을 함께 확인하였다.

---

### 12.2 Localization 안정성 개선

고속 회전 시 map과 localization이 틀어지는 문제가 발생하여 다음을 개선하였다.

* AMCL particle 관련 parameter 조정
* LiDAR scan matching 안정성 확인
* IMU 적용
* EKF 설정 추가
* `/odom/filtered` 사용 검토
* bag 기반 비교 분석

---

### 12.3 Perception 안정성 개선

YOLO 인식 결과가 frame마다 흔들리는 문제를 줄이기 위해 detection filtering을 적용하였다.

예시 구조:

```text
최근 N개의 frame 결과 저장
→ 일정 횟수 이상 동일 상태 감지
→ 최종 위험 상태로 판단
```

이를 통해 순간적인 오탐지를 줄이고 안정적인 감지 결과를 얻고자 하였다.

---

## 13. 실행 명령어 정리

### 13.1 Workspace Build

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

---

### 13.2 LiDAR 실행

```bash
ros2 launch sllidar_ros2 sllidar_launch.py
```

또는 사용한 패키지명에 따라 다음과 같이 실행한다.

```bash
ros2 launch rplidar_ros rplidar.launch.py
```

---

### 13.3 Topic 확인

```bash
ros2 topic list
```

```bash
ros2 topic echo /scan
```

```bash
ros2 topic echo /imu/data
```

```bash
ros2 topic echo /odom
```

---

### 13.4 Node 확인

```bash
ros2 node list
```

---

### 13.5 TF 확인

```bash
ros2 run tf2_tools view_frames
```

```bash
ros2 run tf2_ros tf2_echo map odom
```

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

---

### 13.6 SLAM 실행

```bash
ros2 launch slam_toolbox online_async_launch.py
```

---

### 13.7 Navigation 실행

```bash
ros2 launch nav2_bringup navigation_launch.py
```

또는 프로젝트 launch 파일 사용:

```bash
ros2 launch 패키지명 navigation_launch.py
```

---

### 13.8 Camera 실행

```bash
ros2 run v4l2_camera v4l2_camera_node
```

카메라 topic 확인:

```bash
ros2 topic list | grep image
```

이미지 확인:

```bash
rqt_image_view
```

---

### 13.9 YOLO Node 실행

```bash
ros2 run 패키지명 yolo_pose_node
```

또는 launch 파일 사용:

```bash
ros2 launch 패키지명 yolo_launch.py
```

---

### 13.10 Bag Record

```bash
ros2 bag record /scan /tf /tf_static /odom /odom/filtered /imu/data /cmd_vel
```

---

### 13.11 Bag Play

```bash
ros2 bag play bag파일명
```

---

## 14. 프로젝트를 통해 해결한 핵심 문제

### 문제 1. 고속 회전 시 SLAM이 틀어지는 문제

* 단순 LiDAR 및 odometry 기반 주행에서는 고속 회전 시 yaw 추정 오차가 커졌다.
* 이로 인해 SLAM map이 찌그러지거나 localization이 불안정해졌다.
* IMU를 추가하고 EKF로 센서 융합을 적용하여 방향 추정 안정성을 개선하였다.

---

### 문제 2. USB 장치 번호 변경 문제

* launch를 반복 실행하거나 센서를 재연결하면 `/dev/ttyUSB0`, `/dev/ttyUSB1` 등이 바뀌었다.
* 이로 인해 LiDAR 또는 IMU node가 실행되지 않는 문제가 발생했다.
* `/dev/serial/by-path` 경로를 사용하여 장치 연결 안정성을 높였다.

---

### 문제 3. YOLO node가 camera image를 받지 못하는 문제

* YOLO node의 subscription count가 0으로 나타났다.
* 실제 camera topic과 코드에서 subscribe하는 topic이 일치하지 않는 것이 원인이었다.
* `/v4l2_camera/image_raw` topic을 확인하고 YOLO node의 subscription topic을 수정하였다.

---

### 문제 4. Navigation 속도 증가 후 주행 안정성 저하

* 속도를 높이자 costmap 반응 지연, 장애물 회피 불안정, localization 오차가 발생하였다.
* controller, acceleration, costmap, AMCL parameter를 함께 조정하였다.
* 단순히 속도만 올리는 것이 아니라 센서 처리 속도와 localization 안정성을 함께 고려해야 함을 확인하였다.

---

### 문제 5. Message Dropping 및 처리 부하

* 카메라, LiDAR, YOLO inference가 동시에 실행되면서 message dropping이 발생하였다.
* sensor publish rate, queue size, YOLO 모델 크기, CPU 사용량을 함께 고려해야 했다.
* 불필요한 topic을 줄이고, 경량 모델 및 filtering 구조를 적용하는 방향으로 개선하였다.

---

## 15. 프로젝트 결과

본 프로젝트를 통해 ROS2 기반 UGV에서 다음 기능을 구현하고 검증하였다.

* LiDAR 기반 실내 mapping
* Nav2 기반 목표 지점 자율주행
* AMCL 기반 localization
* IMU 및 EKF 기반 위치 추정 보정
* YOLOv11 Pose 기반 사람 자세 인식
* YOLO 기반 연기 감지
* 카메라, LiDAR, IMU 센서 연동
* ROS2 bag 기반 주행 데이터 기록 및 분석
* 고속 주행 시 발생하는 SLAM/Localization 문제 원인 분석
* USB serial, topic mismatch, package not found, node not found 등 실제 로봇 개발 중 발생한 오류 해결

---

## 16. 배운 점

이번 프로젝트를 통해 단순히 ROS2 패키지를 실행하는 것뿐만 아니라, 실제 로봇 시스템에서 발생하는 센서 연결 문제, TF 문제, topic mismatch, Navigation parameter 튜닝, perception node 처리 부하 등을 직접 경험하였다.

특히 고속 주행 상황에서는 Navigation parameter만 수정하는 것으로는 한계가 있으며, LiDAR scan, odometry, IMU, EKF, AMCL, costmap이 모두 함께 안정적으로 동작해야 한다는 점을 확인하였다.

또한 YOLO 기반 perception 기능을 ROS2에 연결하면서 AI 모델의 추론 결과를 실제 로봇 시스템의 topic 구조와 결합하는 방법을 익혔다.

---

## 17. 향후 개선 방향

향후 프로젝트를 개선한다면 다음 기능을 추가할 수 있다.

* YOLO 모델 경량화 및 Jetson 최적화
* IMU calibration 자동화
* `/odom/filtered` 기반 Navigation 완전 적용
* 관리자 알림 시스템 고도화
* Web dashboard 연동
* 위험 상황별 로그 저장
* SLAM/Localization RMSE 자동 계산 스크립트 작성
* 주행 속도별 성능 비교 자동화
* 센서 연결 상태 진단 launch 추가
* USB 장치 udev rule 설정을 통한 포트 고정

---

## 18. 핵심 키워드

`ROS2` `UGV` `Navigation2` `SLAM` `AMCL` `EKF` `robot_localization` `LiDAR` `IMU` `YOLOv11` `Pose Detection` `Smoke Detection` `OpenCV` `cv_bridge` `ROS2 Bag` `TF` `Costmap` `Autonomous Driving`
