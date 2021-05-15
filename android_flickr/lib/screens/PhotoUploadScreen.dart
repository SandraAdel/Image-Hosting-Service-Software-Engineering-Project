//out of the box imports
import 'package:flutter/material.dart';
import 'dart:typed_data';

//Photo upload screen where user adds image info before uploading it to the server
class PhotoUploadScreen extends StatefulWidget {
  /// The headedBitmap from the Photo edit screen is passed to this widget through the constructor
  final Uint8List headedBitmap;
  PhotoUploadScreen(this.headedBitmap);
  @override
  _PhotoUploadScreenState createState() => _PhotoUploadScreenState();
}

class _PhotoUploadScreenState extends State<PhotoUploadScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color.fromARGB(255, 242, 242, 242),
      appBar: AppBar(
        backgroundColor: Color.fromARGB(255, 56, 56, 56),
        leading: IconButton(
          icon: Icon(Icons.keyboard_backspace_rounded),
          onPressed: () {
            Navigator.of(context).pop();
          },
        ),
        actions: [
          Align(
            alignment: Alignment.centerLeft,
            child: Padding(
              padding: EdgeInsets.only(
                right: 10,
              ),
              child: Container(
                height: 35,
                decoration: BoxDecoration(
                  border: Border.all(
                    color: Colors.white,
                    width: 2,
                  ),
                ),
                child: TextButton(
                  onPressed: () {},
                  child: Text(
                    'Post',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                    ),
                  ),
                ),
              ),
            ),
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.only(
          left: 20.0,
          right: 20.0,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              height: 35,
            ),
            Container(
              height: 100,
              width: 100,
              child: Image.memory(
                widget.headedBitmap,
                fit: BoxFit.cover,
              ),
            ),
            SizedBox(
              height: 35,
            ),
            TextFormField(
              maxLength: 100,
              decoration: InputDecoration(
                hintText: 'Title...',
              ),
            ),
            SizedBox(
              height: 5,
            ),
            TextFormField(
              decoration: InputDecoration(
                hintText: 'Description...',
              ),
            ),
            SizedBox(
              height: 15,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Icon(
                  Icons.location_on_outlined,
                  color: Colors.grey,
                ),
                SizedBox(
                  width: 10,
                ),
                Text('Location'),
              ],
            ),
            SizedBox(
              height: 15,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Icon(
                  Icons.filter_none_rounded,
                  color: Colors.grey,
                ),
                SizedBox(
                  width: 10,
                ),
                Text('Album'),
              ],
            ),
            SizedBox(
              height: 15,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Icon(
                  Icons.label_outlined,
                  color: Colors.grey,
                ),
                SizedBox(
                  width: 10,
                ),
                Text('Tags'),
              ],
            ),
            SizedBox(
              height: 15,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Icon(
                  Icons.lock_open_sharp,
                  color: Colors.grey,
                ),
                SizedBox(
                  width: 10,
                ),
                Text('Public'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
