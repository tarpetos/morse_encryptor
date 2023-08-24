from morse_encryptor.morse_window import Window


def main():
    window_object = Window()
    window_object.title('Morse (De)Coder')
    window_object.geometry('500x200')
    window_object.mainloop()


if __name__ == '__main__':
    main()
