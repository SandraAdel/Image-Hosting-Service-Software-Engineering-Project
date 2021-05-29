import 'package:flutter/material.dart';
import 'package:android_flickr/widgets/public_view_grid.dart';

class GroupsTabBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.white,
          elevation: 0,
          toolbarHeight: MediaQuery.of(context).size.height / 14.2,
          automaticallyImplyLeading: false,
          bottom: TabBar(
            isScrollable: false,
            indicatorColor: Colors.black,
            labelColor: Colors.black,
            unselectedLabelColor: Colors.grey,
            tabs: [
              Tab(
                text: "Photos",
              ),
              Tab(
                text: "Discussions",
              ),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            PublicViewGrid(),
            Column(
              children: <Widget>[
                Padding(padding: EdgeInsets.all(10)),
                Center(
                  child: OutlineButton(
                    onPressed: () {},
                    child: Text(
                      'New Discussion',
                      style: TextStyle(
                        fontSize: 20,
                      ),
                    ),
                    borderSide: BorderSide(
                      color: Colors.black,
                      style: BorderStyle.solid,
                      width: 1.5,
                    ),
                  ),
                  //heightFactor: 2,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
