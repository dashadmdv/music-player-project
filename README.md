# music-player-project
This is a music player with recommendations system that recreates some Spotify features. That project is my university coursework on the subject "Object-oriented programming (OOP)".

Development will be held in **4 main stages**:
<ol>
  <li>Simple CLI player
  <p>This stage is aimed at app skeleton realization. The vast majority of app logic will already be implemented here.</p></li>
  <li>Adding custom serialization&deserialization
  <p>This stage mainly exists for educational purposes. It can take place because the data in my app is mostly fetched in the JSON format. However, the plugin itself will be developed in a different repository (the link will be provided later).</p></li>
  <li>Database integration
  <p>There the project will be slightly modified to be able to work with NoSQL database or a cloud storage (this point is still to be determined). Also some kind of code cleanup is possible.</p></li>
  <li>GUI  implementation
  <p>The aim of this final stage is to make app user friendly and, of course, beautiful. The GUI "role model" will be the original Spotify app. To animate my project i will use Python Kivy framework. I am aiming to make desktop and mobile (android) app.</p></li>
</ol>

### Technical specifications
**Use-Case diagram**

 ![Use-Case](https://user-images.githubusercontent.com/69718734/230737732-8d741807-224a-4d81-a93d-76525b05d290.png)
 
 All the content such as music, albums, playlists, etc. will be fetched through Spotify API. Because of this only **30-second previews** will be available. Also the user can listen to the music from local storage and change its metadata (name, artist, cover).
 
 **Class diagram**
 
 ![Class diagram](https://user-images.githubusercontent.com/69718734/230737884-ea1e2aef-ab11-41fd-887e-03151cf78220.png)


**The project is in process so this README, diagrams and, of course, the repository will be changing.**
