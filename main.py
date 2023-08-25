from morse_encryptor.morse_window import Window

DEFAULT_SIZE: tuple = (500, 200)


def main():
    window_object: Window = Window()
    window_object.title('Morse (De)Coder')
    window_object.geometry(f'{DEFAULT_SIZE[0]}x{DEFAULT_SIZE[1]}')
    window_object.minsize(*DEFAULT_SIZE)
    window_object.mainloop()


if __name__ == '__main__':
    main()
