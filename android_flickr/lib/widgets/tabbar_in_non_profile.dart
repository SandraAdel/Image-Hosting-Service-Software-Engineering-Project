import 'package:android_flickr/widgets/non_profile_public.dart';
import 'package:flutter/material.dart';

class TabbarInNonProfile extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.white,
          elevation: 0,
          titleSpacing: 0,
          toolbarHeight: MediaQuery.of(context).size.height / 14,
          //bottomOpacity: ,
          automaticallyImplyLeading: false,
          bottom: TabBar(
            labelColor: Colors.black,
            unselectedLabelColor: Colors.grey,
            //isScrollable: true,
            tabs: [
              Tab(
                text: "Public",
              ),
              Tab(
                text: "album",
              ),
              Tab(
                text: "Groups",
              ),
              Tab(
                text: "about",
              ),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            NonProfilePublic(),
            Center(
              child: Text("no Albums"),
            ),
            Center(
              child: Text("no notifications"),
            ),
            Center(
              child: Text("no camera"),
            ),
          ],
        ),
      ),
    );
  }
}
