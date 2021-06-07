import 'package:flutter/material.dart';
import '../screens/click_on_image_screen.dart';
import '../providers/flickr_post.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';
// import '../providers/flickr_posts.dart';
// import 'package:provider/provider.dart';

/// Displays list of the photos that the user search for.
class SearchPhotos extends StatelessWidget {
  final photosSearchResult;
  void clickOnImageScreen(
      BuildContext ctx, List<PostDetails> postsToDisplay, int index) {
    Navigator.of(ctx).pushNamed(
      ClickOnImageScreen.routeName,
      arguments: {
        'postDetails': postsToDisplay,
        'isFromPersonalProfile': false,
        'explorePosts': postsToDisplay,
        'postIndex': index,
        'ExORPup': 'explore'
      },
    );
  }

  SearchPhotos(this.photosSearchResult);
  @override
  Widget build(BuildContext context) {
    /// Contains the list of the photos that came from the search result if any.
    //final postsToDisplay = Provider.of<Posts>(context).posts;
    final postsToDisplay = photosSearchResult;
    return StaggeredGridView.countBuilder(
      crossAxisCount: 4,
      padding: EdgeInsets.all(7),
      itemCount: postsToDisplay.length,
      itemBuilder: (context, index) {
        return InkWell(
          onTap: () {
            clickOnImageScreen(context, postsToDisplay, index);
          },
          child: Image.network(
            postsToDisplay[index].postImageUrl,
            fit: BoxFit.fill,
          ),
        );
      },
      staggeredTileBuilder: (int index) =>
          new StaggeredTile.count(2, index.isEven ? 2 : 1),
      mainAxisSpacing: 4.0,
      crossAxisSpacing: 4.0,
    );
  }
}
