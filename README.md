## Intro
This is a python script which scans android xml layout file and generate java code that create a static `ContentView` class.

## Concept
Seeing views inside of activity as member variables makes me uncomfortable. They are members of "ContentView" of the activity,
or `Window`. That's why I use this little pattern for almost all my activities, that is, creating a `ContentView` static class
for every layout. much like famous "ViewHolder" pattern.

## Example
```xml
<RelativeLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    >

    <TextView
        android:id="@+id/tv"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        />
</RelativeLayout>
```

```java
public class MainActivity {

    ContentView content;
    
    @Override protected void onCreate(Bundle savedInstanceState) {
        content = ContentView.attachTo(getWindow());
    }

    private static class ContentView {
        public static final int LAYOUT_ID = R.layout.activity_main; 

        public View root;
        public TextView tv;

        public ContentView(View v) {
            this.root = v;
            this.tv = (TextView) root.findViewById(R.id.tv);
        }

        public static ContentView attachTo(Window window) {
            View v = LayoutInflater.from(window.getContext()).inflate(LAYOUT_ID, null);
            window.setContentView(v);
            return new ContentView(v);
        }
    }
}
```

## Further
If your layout is very complex, you can create static class inside the `ContentView` class
to manage the complexity. Thus you can access your views like `content.layoutSettings.layoutMobile.cb`,
autocomplete of IDE will provide information about what are the views inside this layout.