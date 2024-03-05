import customtkinter
import tkinter as tk 
from makepl import * 

customtkinter.set_appearance_mode("Dark")  
customtkinter.set_default_color_theme("green")

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("960x540")
app.title("Workout Playlist Generator")

title = customtkinter.CTkLabel(app, text="Insert a Spotify song link")
title.pack(padx=10, pady=10)

url_entered = tk.StringVar()
song_link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_entered)
song_link.pack()


def create_button_pushed():
    inputted_link = song_link.get().strip()
    try:
        track_uri = get_track_uri(inputted_link)
        song_info = display_input_song(track_uri)

        similar_track_uris = get_similar_track_uris(track_uri)
        songs_out = display_similar_songs(similar_track_uris)

        results_label.configure(text="Here are the songs for your workout playlist:")
        playlist_label.configure(text=''.join(songs_out))
    except:
        results_label.configure(text="Invalid Spotify song link!")
        


# create playlist button
create_button = customtkinter.CTkButton(app, text="Create Playlist", command=create_button_pushed)
create_button.pack(padx=10, pady=10)


# results
results_label = customtkinter.CTkLabel(app, text="")
results_label.pack(padx=10, pady=10)


# playlist 
playlist_label = customtkinter.CTkLabel(app, text="")
playlist_label.pack(padx=10, pady=10)




# run app 
app.mainloop()