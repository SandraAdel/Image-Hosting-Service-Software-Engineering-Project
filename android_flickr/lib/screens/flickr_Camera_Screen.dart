import 'dart:io';
import 'dart:math';

import 'package:camerawesome/models/orientations.dart';
import 'package:flutter/material.dart';
import 'package:camerawesome/camerawesome_plugin.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:photo_manager/photo_manager.dart';
// import 'package:gallery_saver/gallery_saver.dart';
import 'package:image_gallery_saver/image_gallery_saver.dart';

import './pickFromGallery_Screen.dart';

enum UserFlashMode {
  always,
  auto,
  never,
}

class FlickrCameraScreen extends StatefulWidget {
  @override
  _FlickrCameraScreen createState() => _FlickrCameraScreen();
}

class _FlickrCameraScreen extends State<FlickrCameraScreen>
    with TickerProviderStateMixin {
  //Notifiers
  ValueNotifier<CameraFlashes> _switchFlash = ValueNotifier(CameraFlashes.NONE);
  ValueNotifier<Sensors> _sensor = ValueNotifier(Sensors.BACK);
  ValueNotifier<CaptureModes> _captureMode = ValueNotifier(CaptureModes.PHOTO);
  ValueNotifier<Size> _photoSize = ValueNotifier(Size(3840, 2160));
  ValueNotifier<double> _zoom = ValueNotifier(0);
  // Controllers
  PictureController _pictureController = new PictureController();
  VideoController _videoController = new VideoController();

  // List of all images on the device (customized to only load the first image, the recent image)
  List<AssetEntity> galleryList;
  // the last image stored on the device
  File recentImage;

// bool that reflects the user choice of either photo or video
  bool isVideoMode = false;

  //index of the camera mode chosen by user, 0 = back camera, 1 = front.
  int inUseCamera;
  // flash mode chosen by user.
  UserFlashMode flashMode = UserFlashMode.auto;

  @override
  void dispose() {
    // previewStreamSub.cancel();
    _photoSize.dispose();
    _captureMode.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    SystemChrome.setEnabledSystemUIOverlays([SystemUiOverlay.bottom]);
    initGallary();
  }

  @override
  Widget build(BuildContext context) {
    final deviceHeight = MediaQuery.of(context).size.height;
    final deviceWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: Color.fromARGB(255, 31, 31, 33),
      body: Container(
        height: deviceHeight,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              height: deviceHeight * 0.45,
              child: Stack(
                children: [
                  CameraAwesome(
                    testMode: false,
                    selectDefaultSize: (List<Size> availableSizes) {
                      // print(availableSizes.toString());
                      return availableSizes[0];
                    },
                    onOrientationChanged:
                        (CameraOrientations newOrientation) {},
                    zoom: _zoom,
                    sensor: _sensor,
                    photoSize: _photoSize,
                    switchFlashMode: _switchFlash,
                    captureMode: _captureMode,
                    orientation: DeviceOrientation.portraitUp,
                    fitted: false,
                  ),
                  Padding(
                    padding:
                        EdgeInsets.only(top: 20, left: deviceWidth * 0.825),
                    child: Container(
                      height: 50,
                      width: 50,
                      // padding: EdgeInsets.all(10),
                      color: Colors.black38,
                      child: Icon(
                        Icons.close,
                        color: Colors.white,
                        size: 33,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Stack(
                  children: [
                    Container(
                      color: Color.fromARGB(255, 21, 21, 21),
                      height: deviceHeight * 0.09,
                    ),
                    Padding(
                      padding: EdgeInsets.only(top: deviceHeight * 0.025),
                      child: cameraModeButton('assets/images/CameraMode.png'),
                    ),
                    Align(
                      alignment: Alignment.topRight,
                      child: Padding(
                        padding: EdgeInsets.only(top: deviceHeight * 0.025),
                        child: flashModeButton(
                          flashModeSwitchCase(),
                        ),
                      ),
                    ),
                  ],
                ),
                Stack(
                  children: [
                    Container(
                      color: Color.fromARGB(255, 12, 12, 12),
                      height: deviceHeight * 0.125,
                    ),
                    Align(
                      child: GestureDetector(
                        onTap: () {
                          takePhoto();
                        },
                        child: Container(
                          width: 60,
                          height: deviceHeight * 0.125,
                          decoration: BoxDecoration(
                            color: isVideoMode
                                ? Color.fromARGB(255, 167, 23, 23)
                                : Colors.white,
                            shape: BoxShape.circle,
                          ),
                        ),
                      ),
                      alignment: Alignment.center,
                    ),
                    Align(
                      child: Container(
                        width: 8,
                        height: deviceHeight * 0.125,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                      ),
                      alignment:
                          isVideoMode ? Alignment(-0.2, 0) : Alignment(0.2, 0),
                    ),
                    Align(
                      child: Container(
                        padding: EdgeInsets.only(top: deviceHeight * 0.045),
                        width: 30,
                        child: GestureDetector(
                          onTap: () {
                            setState(() {
                              isVideoMode = false;
                            });
                          },
                          child: Image.asset(
                            isVideoMode
                                ? 'assets/images/Photo_Grey.png'
                                : 'assets/images/Photo.png',
                          ),
                        ),
                      ),
                      alignment: Alignment(0.32, 0),
                    ),
                    Align(
                      child: Container(
                        padding: EdgeInsets.only(top: deviceHeight * 0.045),
                        width: 30,
                        child: GestureDetector(
                          onTap: () {
                            setState(() {
                              isVideoMode = true;
                            });
                          },
                          child: Image.asset(
                            isVideoMode
                                ? 'assets/images/Video.png'
                                : 'assets/images/Video_Grey.png',
                          ),
                        ),
                      ),
                      alignment: Alignment(-0.32, 0),
                    ),
                    Align(
                      child: Container(
                        padding: EdgeInsets.only(top: deviceHeight * 0.0525),
                        width: 35,
                        height: 70,
                        child: GestureDetector(
                          onTap: () {
                            Navigator.pushReplacement(
                                context,
                                MaterialPageRoute(
                                    builder: (BuildContext context) =>
                                        PhotoGallery()));
                          },
                          child: recentImage == null
                              ? Container(
                                  color: Colors.grey,
                                )
                              : Image.file(
                                  recentImage,
                                  fit: BoxFit.cover,
                                ),
                        ),
                      ),
                      alignment: Alignment(-0.9, 0),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future initGallary() async {
    await PhotoManager.requestPermission();
    PhotoManager.clearFileCache();
    List<AssetPathEntity> list = await PhotoManager.getAssetPathList(
      onlyAll: true,
      filterOption: FilterOptionGroup(
        orders: [
          OrderOption(
            type: OrderOptionType.createDate,
          )
        ],
      ),
    );

    //only get the first two images, not anymore are needed in this view
    galleryList = await list[0].getAssetListRange(start: 0, end: 1);

    galleryList[0].file.then((value) {
      setState(() {
        recentImage = value;
      });
    });
  }

  //press to change camera mode, front and back
  Widget cameraModeButton(String imagePath) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.05,
      child: GestureDetector(
        onTap: () {
          if (inUseCamera == 1) {
            setState(() {
              inUseCamera = 0;
            });
            _sensor.value = Sensors.BACK;
          } else {
            setState(() {
              inUseCamera = 1;
            });
            _sensor.value = Sensors.FRONT;
          }
          // initCamera(allCameras[inUseCamera]).then((value) {});
        },
        child: inUseCamera == 0
            ? Padding(
                padding: const EdgeInsets.only(left: 10),
                child: Image.asset(
                  imagePath,
                  width: 30,
                  height: 30,
                ),
              )
            : Padding(
                padding: const EdgeInsets.only(left: 40),
                child: Transform(
                  transform: Matrix4.rotationY(pi),
                  child: Image.asset(
                    imagePath,
                    width: 30,
                    height: 30,
                  ),
                ),
              ),
      ),
    );
  }

  Widget flashModeButton(String imagePath) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.05,
      child: GestureDetector(
        onTap: () {
          if (flashMode == UserFlashMode.always) {
            // cameraController.setFlashMode(FlashMode.off);
            setState(() {
              flashMode = UserFlashMode.never;
            });
            _switchFlash.value = CameraFlashes.NONE;
            return;
          }
          if (flashMode == UserFlashMode.never) {
            // cameraController.setFlashMode(FlashMode.auto);
            setState(() {
              flashMode = UserFlashMode.auto;
            });
            _switchFlash.value = CameraFlashes.AUTO;
            return;
          }
          if (flashMode == UserFlashMode.auto) {
            // cameraController.setFlashMode(FlashMode.always);
            setState(() {
              flashMode = UserFlashMode.always;
            });
            _switchFlash.value = CameraFlashes.ALWAYS;
            return;
          }
        },
        child: Padding(
          padding: const EdgeInsets.only(right: 8.0),
          child: Image.asset(
            imagePath,
            width: 35,
            height: 35,
          ),
        ),
      ),
    );
  }

  String flashModeSwitchCase() {
    switch (flashMode) {
      case UserFlashMode.always:
        return 'assets/images/FlashAlways.png';
        break;
      case UserFlashMode.auto:
        return 'assets/images/FlashAuto.png';
        break;
      case UserFlashMode.never:
        return 'assets/images/FlashNever.png';
        break;
      default:
        return 'assets/images/FlashAuto.png';
    }
  }

  Future takePhoto() async {
    // final Directory tempDir = await getTemporaryDirectory();
    // final filePath =
    //     await Directory('${tempDir.path}/cameraphoto').create(recursive: true);

    // // _pictureController.takePicture('${filePath.path}/fpcamera.jpg').then(
    // //       (value) {},
    // //     );
    // await _pictureController.takePicture('${tempDir.path}/myimage.jpg');
    final Directory tempDir = await getTemporaryDirectory();
    final imageDir =
        await Directory('${tempDir.path}/test').create(recursive: true);
    final String filePath =
        '${imageDir.path}/${DateTime.now().millisecondsSinceEpoch}.jpg';
    await _pictureController.takePicture(filePath);

    if (filePath != null) {
      // GallerySaver.saveImage(filePath).then((value) => {
      //       setState(() {
      //         print('image saved!');
      //       })
      //     });
      final result = await ImageGallerySaver.saveFile(filePath);
      print(result);
    } else {
      print('Null path');
    }
  }
}