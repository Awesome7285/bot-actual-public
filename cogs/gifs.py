import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
from .func.funcs import squash_text, IncorrectInputError, text_image
from PIL import Image, ImageDraw, ImageFont, ImageSequence, UnidentifiedImageError
#from imagetext_py import FontDB, TextAlign, Writer, EmojiOptions, Paint, Font
#from imagetext_py.lib import EmojiOptions, FontDB
import os
import requests

#FontDB.SetDefaultEmojiOptions(EmojiOptions(parse_discord_emojis=True))
#FontDB.LoadFromDir(".")

#font = FontDB.Query("coolvetica japanese")

class Gifs(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    '''
    def gif_text(self, gif, top_text, bottom_text):
        images = []
        with Image.open(f'gifs/{gif}.gif') as im:
            im.seek(1)  # skip to the second frame

            try:
                while 1:
                    im.seek(im.tell() + 1)
                    images.append(im)
                    # do something to im
            except EOFError:
                pass  # end of sequence
        
        # i = 1
        # f_list = ImageSequence.Iterator(im)
        # for frame in f_list:
        #     # Text stuff
        #     #frame = text_image(frame, top_text, 'white', 32, (frame.width/2, 32), 'ma', 'impact')
        #     #frame = text_image(frame, bottom_text, 'white', 32, (frame.width/2, frame.height-48), 'ma', 'impact')

        #     images.append(frame)
        #     i += 1
        #     frame.show()
        
        
        images[0].save(f'gifs/TEMP.gif', save_all=True, append_images=images[1:], optimize=True, loop=0, duration=len(images))
    '''
            
    def add_text(self, image_path, top_text, bottom_text):
        # Open the base image
        try:
            image = Image.open(f"gifs/default/{image_path}.png")
        except FileNotFoundError:
            image = Image.open(f"gifs/default/{image_path}.gif")

        # Get the width and height of the base image
        width, height = image.size

        # Calculate the maximum font size that will fit both texts
        max_font_size = int(min(width, height) * 0.1)
        font = ImageFont.truetype("impact.ttf", max_font_size)

        # Reduce the font size until both texts fit in the image
        top_text_size = font.getsize(top_text)
        bottom_text_size = font.getsize(bottom_text)
        while top_text_size[0] > 0.8 * width or bottom_text_size[0] > 0.8 * width:
            max_font_size -= 1
            top_text_size = font.getsize(top_text)
            bottom_text_size = font.getsize(bottom_text)

        # Calculate the position of the top text
        top_text_x = (width - top_text_size[0]) / 2
        top_text_y = 16 #font.getsize(top_text)[1]

        # Calculate the position of the bottom text
        bottom_text_x = (width - bottom_text_size[0]) / 2
        bottom_text_y = height - bottom_text_size[1] - 16 #font.getsize(bottom_text)[1]

        # Draw the text on the image
        draw = ImageDraw.Draw(image)
        draw.text((top_text_x, top_text_y), top_text, font=font, fill=(255, 255, 255))
        draw.text((bottom_text_x, bottom_text_y), bottom_text, font=font, fill=(255, 255, 255))

        # Save the image with the text added
        image.save('gifs/temp/TEMP.gif')

    def add_text_to_gif(self, input_path, top_text=None, bottom_text=None, text_colour='white'):
        with Image.open(input_path) as img:
            frames = []

            # Calculate the maximum font size that will fit both texts
            font_size = int(img.height * 0.1)
            font = ImageFont.truetype("impact.ttf", font_size)

            # Outline Colour
            if text_colour in ['black', '#000000']:
                outline_colour = 'white'
            else:
                outline_colour = 'black'

            for frame in ImageSequence.Iterator(img):
                # Copy each frame to a new image
                new_frame = frame.copy()
                new_frame = new_frame.convert('RGBA')

                # Create a drawing context and set the font
                draw = ImageDraw.Draw(new_frame)

                max_text_width = frame.width - 20

                # Calculate the position to center the top text at the top of the frame
                if top_text:
                    top_x = frame.width // 2
                    top_y = 10

                    # Split the top text into multiple lines if it's too long to fit on one line
                    top_text_lines = []
                    top_words = top_text.split()
                    top_current_line = top_words.pop(0)
                    for word in top_words:
                        test_line = top_current_line + ' ' + word
                        if draw.textlength(test_line, font=font) <= max_text_width:
                            top_current_line = test_line
                        else:
                            top_text_lines.append(top_current_line)
                            top_current_line = word
                    top_text_lines.append(top_current_line)

                    # Add the top text to the frame
                    for line in top_text_lines:
                        top_text_width = draw.textlength(line, font=font)
                        top_x = (frame.width - top_text_width) // 2
                        draw.text((top_x - 1, top_y - 1), line, fill=outline_colour, font=font)
                        draw.text((top_x + 1, top_y - 1), line, fill=outline_colour, font=font)
                        draw.text((top_x + 1, top_y + 1), line, fill=outline_colour, font=font)
                        draw.text((top_x - 1, top_y + 1), line, fill=outline_colour, font=font)
                        draw.text((top_x, top_y), line, fill=text_colour, font=font)
                        top_y += font_size + 5

                # Calculate the position to center the bottom text at the bottom of the frame
                if bottom_text:
                    bottom_x = frame.width // 2
                    #bottom_y = frame.height - font_size - 10

                    # Split the bottom text into multiple lines if it's too long to fit on one line
                    bottom_text_lines = []
                    bottom_words = bottom_text.split()
                    bottom_current_line = bottom_words.pop(0)
                    for word in bottom_words:
                        test_line = bottom_current_line + ' ' + word
                        if draw.textlength(test_line, font=font) <= max_text_width:
                            bottom_current_line = test_line
                        else:
                            bottom_text_lines.append(bottom_current_line)
                            bottom_current_line = word
                    bottom_text_lines.append(bottom_current_line)

                    # Add the bottom text to the frame
                    for line_num, line in enumerate(bottom_text_lines):
                        bottom_text_width = draw.textlength(line, font=font)
                        bottom_y = (frame.height - font_size - 10) - ((font_size + 5) * (len(bottom_text_lines) - line_num - 1))
                        bottom_x = (frame.width - bottom_text_width) // 2
                        draw.text((bottom_x - 1, bottom_y - 1), line, fill=outline_colour, font=font)
                        draw.text((bottom_x + 1, bottom_y - 1), line, fill=outline_colour, font=font)
                        draw.text((bottom_x + 1, bottom_y + 1), line, fill=outline_colour, font=font)
                        draw.text((bottom_x - 1, bottom_y + 1), line, fill=outline_colour, font=font)
                        draw.text((bottom_x, bottom_y), line, fill=text_colour, font=font)

                frame.quantize(colors=255) # Always fucks with the colours even if it responds with png

                # Append the modified frame to the list of frames
                frames.append(new_frame) 

            # Save the modified frames as a new animated GIF
            if len(frames) > 1:
                frames[0].save('./gifs/temp/TEMP.gif', save_all=True, append_images=frames[1:], loop=0, duration=img.info['duration'])
            else:
                frames[0].save('./gifs/temp/TEMP.gif')
            print("Text added and new GIF saved successfully.")

    # def imagetextpy_text_gif(self, input_path, top_text=None, bottom_text=None, text_colour='white'):
    #     with Image.open(input_path) as im:
    #         with Writer(im) as w:
    #             w.draw_text_wrapped(
    #                 text="hello from python 😓 lol, <:blobpain:739614945045643447> " \
    #                     "ほまみ <:chad:682819256173461522><:bigbrain:744344773229543495> " \
    #                     "emojis workin",
    #                 x=256, y=256,
    #                 ax=0.5, ay=0.5,
    #                 width=500,
    #                 size=90,
    #                 font=font,
    #                 fill=Paint.Color((0, 0, 0, 255)),
    #                 align=TextAlign.Center,
    #                 stroke=2.0,
    #                 stroke_color=Paint.Rainbow((0.0,0.0), (256.0,256.0)),
    #                 draw_emojis=True
    #             )
    #         im.save('./gifs/temp/TEMP.gif')

    def save_gif_from_tenor(self, url, save_path):
        error = None
        try:
            response = requests.get(url)
            response.raise_for_status()

            with open(save_path, 'wb') as file:
                file.write(response.content)

            # Check download is an image
            Image.open(save_path)
                
            print("GIF saved successfully.")
        except Exception as e:
            print(f"Error while saving GIF: {e}")
            error = e
        return error

    @nextcord.slash_command(description="Create a gif with text",
                            #guild_ids=[1039880876982546504]
                            )
    async def meme(self, interaction: Interaction, 
                   upload_img:nextcord.Attachment = SlashOption(required=False, default=None, name='upload'), 
                   default_img:str = SlashOption(choices=[f for f in os.listdir('./gifs/default/')], required=False, default=None, name='preset'),
                   url_img:str = SlashOption(required=False, default=None, name='url'), 
                   top_text:str = SlashOption(required=False, default=None), 
                   bottom_text:str = SlashOption(required=False, default=None),
                   colour:str = SlashOption(required=False, default=None),
                   output_type:str = SlashOption(required=False, choices=['gif', 'png'], default='gif')):
        # Standard
        await interaction.response.defer()
        print("Command Meme called by: ", interaction.user.id)
        
        if upload_img:
            if 'image' in upload_img.content_type:
                gif_name = upload_img.filename
                input_path = f'./gifs/temp/{gif_name}'
                await upload_img.save(input_path)
                print("Uploaded Image: ", input_path)
            else:
                await interaction.send("You must upload an Image or GIF file.")
                return
        elif default_img:
            input_path = f'./gifs/default/{default_img}'
            gif_name = default_img
        elif url_img:
            gif_name = url_img.split('/')[-1]
            input_path = f'./gifs/temp/{gif_name}'
            print("Downloading Image: ", url_img, "\nSaving To: ", input_path)

            error = self.save_gif_from_tenor(url_img, input_path)
            if type(error) == UnidentifiedImageError:
                await interaction.send("Image/GIF could not be recognised from that URL. If you are using tenor, make sure to copy the link from media.tenor.com instead.")
                return
            elif error:
                await interaction.send("An error occured reaching that URL.")
                #await interaction.send("GIF URL must be in media.tenor.com format. (Open the URL in a browser, then press right click and copy image address)")
                return
        else:
            await interaction.send("You need to specify an image.")
            return

        # Add the text to the GIF path
        self.add_text_to_gif(input_path, top_text=top_text, bottom_text=bottom_text, text_colour=colour)

        gif_name = gif_name[:gif_name.find('.')+1] + output_type
        file = nextcord.File(f"./gifs/temp/TEMP.gif", filename=gif_name)
        await interaction.send('Meme Created!', file=file)

        # Delete the downloaded image
        if url_img or upload_img:
            os.remove(input_path)

# Setup Cog into main bot
def setup(client):
    client.add_cog(Gifs(client))