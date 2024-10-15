from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import random
import os

class DiceRollerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.roll_results = []  # Initialize roll_results as an empty list

    def build(self):
        #Adjust window size to accommodate content
        Window.size = (1000, 800)

        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Create a title label
        self.title_label = Label(text='Dice Roller', font_size=50, size_hint=(1, 0.2), halign='center')
        self.title_label.bind(size=self.title_label.setter('text_size'))  # Allow text wrapping
        self.layout.add_widget(self.title_label)

        # Saved information section
        self.saved_info_label = Label(text='', font_size=20, size_hint=(1, 0.2), halign='center')
        self.saved_info_label.bind(size=self.saved_info_label.setter('text_size'))  # Allow text wrapping
        self.layout.add_widget(self.saved_info_label)

        # Dice type selector
        self.dice_spinner = Spinner(
            text='D6', values=('D4', 'D6', 'D8', 'D10', 'D12', 'D20'),
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.dice_spinner)

        # Number of dice input
        self.dice_count_input = TextInput(
            text='',
            multiline=False,
            hint_text='Number of dice to roll',
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.dice_count_input)

        # Horizontal layout for displaying dice images and labels
        self.dice_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        self.layout.add_widget(self.dice_layout)

        # Create a label to display the result
        self.result_label = Label(text='Roll the Dice!', font_size=25, size_hint=(1, 0.2))
        self.layout.add_widget(self.result_label)

        # Create a button to roll the dice
        self.roll_button = Button(text='Roll', font_size=30, size_hint=(1, 0.2))
        self.roll_button.bind(on_press=self.roll_dice)
        self.layout.add_widget(self.roll_button)

        # Create a button to save dice names and descriptions
        self.save_button = Button(text='Save', font_size=30, size_hint=(1, 0.2))
        self.save_button.bind(on_press=self.save_dice_info)
        self.layout.add_widget(self.save_button)

        # Create a clear button to reset the inputs
        self.clear_button = Button(text='Clear', font_size=30, size_hint=(1, 0.2))
        self.clear_button.bind(on_press=self.clear_dice_info)
        self.layout.add_widget(self.clear_button)

        # Scrollable layout for rolled numbers
        self.rolled_numbers_layout = GridLayout(cols=1, size_hint_y=None)
        self.rolled_numbers_layout.bind(minimum_height=self.rolled_numbers_layout.setter('height'))
        self.scroll_view = ScrollView(size_hint=(1, 0.5))
        self.scroll_view.add_widget(self.rolled_numbers_layout)
        self.layout.add_widget(self.scroll_view)

        return self.layout

    def roll_dice(self, instance):
        # Start flipping the dice through images
        self.current_flip_index = 0
        self.flip_count = 10

        # Get dice type (e.g., D4, D6, D8)
        dice_type = int(self.dice_spinner.text[1:])
        
        # Number of dice to roll
        try:
            num_dice = int(self.dice_count_input.text)
        except ValueError:
            self.result_label.text = 'Please enter a valid number of dice.'
            return

        # Clear the dice layout before adding new dice images and labels
        self.dice_layout.clear_widgets()

        # Clear the rolled numbers layout before adding new results
        self.rolled_numbers_layout.clear_widgets()

        # Roll the dice and store the results
        self.roll_results = [random.randint(1, dice_type) for _ in range(num_dice)]

        # Add the results to the scrollable layout
        for i, result in enumerate(self.roll_results):
            result_label = Label(text=f'Die {i + 1}: {result}', size_hint_y=None, height=40)
            self.rolled_numbers_layout.add_widget(result_label)

        # Store dice folder
        self.dice_folder = f'D{dice_type}'  # Set folder based on dice type
        dice_files = os.listdir(self.dice_folder)  # Get the dice images in the folder

        # Create a list to hold dice image widgets and results
        self.dice_images = []

        # Initialize dice images in the layout
        for i in range(num_dice):
            # Create a vertical layout for each die
            die_layout = BoxLayout(orientation='vertical', size_hint=(1 / num_dice, 1))
            dice_image = Image(source=os.path.join(self.dice_folder, f'Dice1.png'), size_hint=(1, 0.7))
            die_name_input = TextInput(hint_text='Name', size_hint=(1, 0.25))
            die_description_input = TextInput(hint_text='Description', size_hint=(1, 0.25))

            # Add image and input fields to the die layout
            die_layout.add_widget(dice_image)
            die_layout.add_widget(die_name_input)
            die_layout.add_widget(die_description_input)

            self.dice_images.append((dice_image, die_name_input, die_description_input))
            self.dice_layout.add_widget(die_layout)

        # Initialize flipping state
        self.flip_dice(0)

    def flip_dice(self, dt):
        if self.current_flip_index < self.flip_count:
            # Cycle through random dice images for each dice
            for dice_image, _, _ in self.dice_images:
                random_image = random.choice(os.listdir(self.dice_folder))  # Randomly pick an image
                dice_image.source = os.path.join(self.dice_folder, random_image)
                dice_image.reload()

            self.current_flip_index += 1
            # Schedule the next flip
            Clock.schedule_once(self.flip_dice, 0.1)
        else:
            # After flipping, show the final results for each dice
            for i, (dice_image, _, _) in enumerate(self.dice_images):
                result_image = f'Dice{self.roll_results[i]}.png'
                dice_image.source = os.path.join(self.dice_folder, result_image)
                dice_image.reload()

            # Update the result label to show the results of all dice
            self.result_label.text = f'You rolled: {", ".join(map(str, self.roll_results))}'

    def save_dice_info(self, instance):
        # Check if any dice have been rolled
        if not self.roll_results:
            self.saved_info_label.text = 'Please roll the dice first before saving.'
            return
        
        # Save the names and descriptions of the dice
        saved_info = []
        for i, (_, name_input, description_input) in enumerate(self.dice_images):
            name = name_input.text.strip()
            description = description_input.text.strip()
            if name and description:  # Only save if both fields are filled
                saved_info.append(f'Dice {i + 1}: {name}, Description: {description}')

        # Display the saved information
        if saved_info:
            self.saved_info_label.text = "\n".join(saved_info)
            self.result_label.text = 'Dice information saved!'
        else:
            self.saved_info_label.text = ''
            self.result_label.text = 'Please enter names and descriptions for the dice.'

    def clear_dice_info(self, instance):
        # Clear input fields and saved information
        for _, name_input, description_input in self.dice_images:
            name_input.text = ''
            description_input.text = ''
        self.saved_info_label.text = ''
        self.result_label.text = 'Ready to roll!'

if __name__ == '__main__':
    DiceRollerApp().run()
