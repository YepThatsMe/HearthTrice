from io import BytesIO
from typing import Tuple
from wand.image import Image as WandImage
from wand.drawing import Drawing

from PIL import Image, ImageFont, ImageDraw
import re
from DataTypes import CardMetadata, CardType, ClassType, Rarity

from PIL import Image
from io import BytesIO
from PyQt5.QtCore import QFile

class Validate:

    def has_cyrillic(text):
        return bool(re.search('[\u0400-\u04FF]', text))

class GenerationError(BaseException):
    pass

class VirtualException(BaseException):
    pass

class CardImageGenerator:
    CARDTYPE = 0
    
    RESOURCE_FONT_PATH = r":fonts\Belwe Bd BT Bold.ttf"
    RESOURCE_FONT_C_PATH = r":fonts\Arial.ttf"

    RESOURCE_FONT_DESCR_PATH = r":fonts\FRADMCN.ttf"
    RESOURCE_FONT_DESCR_BOLD_PATH = r":fonts\FRADMCN.ttf"

    BASE_CARD_RESOLUTION = (600,154)
    MAX_NAME_SIZE = 30

    FOUNDATION_PADDING_W = 100
    FOUNDATION_PADDING_H = 100

    def __init__(self) -> None:
        cardtype = CardType(self.CARDTYPE).name
        base_path = f":Cardbuilder\\{cardtype}\\"
        self.RESOURCE_BASECARD_PATH = base_path + f"BASECARDS\\Card_Inhand_{cardtype}_"
        self.RESOURCE_MINION_DROPSHADOW = base_path + f"Card_Inhand_{cardtype}_DropShadow.png"
        self.RESOURCE_MINION_FRAME_MASK = base_path + "mask3.png"
        
        self.RESOURCE_GEM_COMMON_PATH = base_path + f"Card_Inhand_{cardtype}_Gem_Common.png"
        self.RESOURCE_GEM_RARE_PATH = base_path + f"Card_Inhand_{cardtype}_Gem_Rare.png"
        self.RESOURCE_GEM_EPIC_PATH = base_path + f"Card_Inhand_{cardtype}_Gem_Epic.png"
        self.RESOURCE_GEM_LEGENDARY_PATH = base_path + f"Card_Inhand_{cardtype}_Gem_Legendary.png"
        self.RESOURCE_LEGENDARY_DRAGON_PATH = base_path + f"Card_Inhand_{cardtype}_LegendaryDragon.png"
        self.RESOURCE_NAME_BANNER_PATH = base_path + f"Card_Inhand_BannerAtlas_{cardtype}_Title.png"
        self.RESOURCE_DESCRIPTION_BANNER_PATH = base_path + f"Card_Inhand_BannerAtlas_{cardtype}_Text.png"
        self.RESOURCE_TRIBE_PLAQUE_PATH = base_path + f"Card_Inhand_BannerAtlas_{cardtype}_TribePlaque.png"
        self.RESOURCE_MANATEXTURE_PATH = base_path + "manatexture.png"
        self.RESOURCE_ATTACKTEXTURE_PATH = base_path + "attacktexture.png"
        self.RESOURCE_HEALTHTEXTURE_PATH = base_path + "healthtexture.png"

    def generate(self, card_metadata: CardMetadata):
        raise VirtualException("Method was not implemented")

    def generate_base_card(self, class_type: ClassType):
        path = ''
        if class_type is None:
            raise GenerationError("No CardType specified")
        else:
            path = self.RESOURCE_BASECARD_PATH + ClassType(class_type).name + ".png"
        
        self.base_card = self.ImageFromRes(path).convert('RGBA')
        
        self.foundation = Image.new('RGBA', size=(self.base_card.width + self.FOUNDATION_PADDING_W,
                                                    self.base_card.height+ self.FOUNDATION_PADDING_H))

    def generate_framed_picture(self, picture_bytes: bytes, offset: tuple, move_x: int=0, move_y: int=0, zoom: int=0):
        if not picture_bytes:
            picture = Image.new('RGBA', (1,1))
        else:
            picture = Image.open(BytesIO(picture_bytes))
        frame = self.ImageFromRes(self.RESOURCE_MINION_FRAME_MASK).convert('RGBA')
        shadow = self.ImageFromRes(self.RESOURCE_MINION_DROPSHADOW).convert('RGBA')

        p_x, p_y = picture.size
        s_x, s_y = frame.size

        def resize(picture: Image, difference: int = 0) -> Image:

            k = picture.width/picture.height
            if p_x >= p_y:
                # For Horizontal/Square images

                picture = picture.resize( (int(picture.width + difference * k),
                                    int(picture.height + difference )), 
                                    Image.Resampling.LANCZOS)
            else:
                # For Vertical images
                picture = picture.resize( (int(picture.width + difference), 
                                    int(picture.height + difference/k) ), 
                                    Image.Resampling.LANCZOS)

            return picture

        ###### I #####
        # Enlarge low-wide image to match picture-frame size #
        if p_y < s_y:
            picture = resize(picture, frame.height - picture.height)
            
        ###### II #####
        # Enlarge high-narrow image to match picture-frame size #
        elif p_x < s_x:
            picture = resize(picture, frame.width - picture.width)

        if zoom:
            picture = resize(picture, zoom)

        p_x, p_y = picture.size

        crop_x1 = (p_x-s_x)/2
        crop_y1 = (p_y-s_y)/2
        crop_x2 = (p_x-s_x)/2 + s_x
        crop_y2 = (p_y-s_y)/2 + s_y

        picture = picture.crop(box=[crop_x1+move_x, crop_y1+move_y, crop_x2+move_x, crop_y2+move_y])

        if picture.size != frame.size:
            picture = picture.resize(frame.size, Image.Resampling.LANCZOS)

        bc_w, bc_h = self.base_card.size
        f_w, f_h = self.foundation.size
        avatar = Image.composite(picture, self.foundation, frame)
        self.foundation.paste(avatar, (int((f_w-bc_w)/2) + offset[0], int((f_h-bc_h)/2) + offset[1]), mask=avatar)
        self.foundation.paste(shadow, (int((f_w-bc_w)/2) + offset[0], int((f_h-bc_h)/2) + offset[1]), mask=shadow)

        t_offset = ((f_w - bc_w) // 2, ((f_h - bc_h) // 2))
        self.foundation.paste(self.base_card, t_offset, mask=self.base_card)

        return self.foundation

    def generate_name_banner(self, text: str) -> Image:
        background = self.ImageFromRes(self.RESOURCE_NAME_BANNER_PATH).convert('RGBA')

        if not text:
            return background
        
        if len(text) > self.MAX_NAME_SIZE:
            raise RuntimeError("Card name length cannot exceed 30.")

        font = self.RESOURCE_FONT_PATH
        if Validate.has_cyrillic(text):
            font = self.RESOURCE_FONT_C_PATH

        font_size, curve_degree, offset = self.get_text_adjust_params(
            self.get_text_size_for_12px_font(font, text)
        )


        """
        Uses ImageMagik / wand.
        """
        img = WandImage(width=1, height=1, resolution=self.BASE_CARD_RESOLUTION)
        with Drawing() as draw:
            draw.font = font
            draw.font_size = font_size
            
            metrics = draw.get_font_metrics(img, text)
            height, width = int(metrics.text_height), int(metrics.text_width)
            
            img.resize(width=width+15, height=height+30)
            
            # Draw outline 
            draw.fill_color = "black"

            for x in range(4, 9):
                for y in range(4, 9):
                    draw.text(x, height+y, text)

            draw.fill_color = "white"
            draw.font_size = font_size
            
            # Draw name
            draw.text(6, height+6, text)
            draw(img)
            img.virtual_pixel = 'transparent'

            if curve_degree >= 0:
                img.distort('arc', (curve_degree, 0))

            img.format = 'png'
            #CLOSE WAND IMAGE

        text_arc = Image.open(BytesIO(img.make_blob('png'))).convert('RGBA')
        bg_w, bg_h = background.size
        img_w, img_h = text_arc.size        
        t_offset = ((bg_w - img_w) // 2, ((bg_h - img_h) - offset))

        name_banner = self.combine_images(background, text_arc, t_offset)

        return name_banner

    def generate_description_banner(self, text: str) -> Image:
        BANNER_WIDTH = 580
        BANNER_HEIGHT = 300

        descrtiption_banner = self.ImageFromRes(self.RESOURCE_DESCRIPTION_BANNER_PATH).convert('RGBA')

        if not text:
            return descrtiption_banner

        font = self.ImageFontFromRes(self.RESOURCE_FONT_DESCR_PATH, 53)
        font_bold = self.ImageFontFromRes(self.RESOURCE_FONT_DESCR_BOLD_PATH, 53)

        lines_of_text = self.text_wrap(text, font_bold, BANNER_WIDTH)

        if len(lines_of_text) == 1:
            HEIGHT_OFFSET = 100
            FONT_SIZE = 53
            LINE_SPACING_INC = 0
        if len(lines_of_text) == 2:
            HEIGHT_OFFSET = 110
            FONT_SIZE = 52
            LINE_SPACING_INC = 50
        if len(lines_of_text) == 3:
            HEIGHT_OFFSET = 90
            FONT_SIZE = 53
            LINE_SPACING_INC = 50
        if len(lines_of_text) == 4:
            HEIGHT_OFFSET = 60
            FONT_SIZE = 43
            LINE_SPACING_INC = 50
        if len(lines_of_text) == 5:
            HEIGHT_OFFSET = 60
            FONT_SIZE = 34
            LINE_SPACING_INC = 40
        if len(lines_of_text) == 6:
            HEIGHT_OFFSET = 35
            FONT_SIZE = 29
            LINE_SPACING_INC = 35
        if len(lines_of_text) == 7:
            HEIGHT_OFFSET = 35
            FONT_SIZE = 29
            LINE_SPACING_INC = 35
        if len(lines_of_text) == 8:
            HEIGHT_OFFSET = 16
            FONT_SIZE = 29
            LINE_SPACING_INC = 35
        if len(lines_of_text) > 8:
            raise RuntimeError("Card description is too long (max 8 lines)")

        font = self.ImageFontFromRes(self.RESOURCE_FONT_DESCR_PATH, FONT_SIZE)
        font_bold = self.ImageFontFromRes(self.RESOURCE_FONT_DESCR_BOLD_PATH, FONT_SIZE)

        W, H = (BANNER_WIDTH, BANNER_HEIGHT)
        image = Image.new('RGBA', (W, H))

        next_line_spacing = 0
        current_font = font
        for line in lines_of_text:

            limage = Image.new('RGBA', (W, H))
            ldraw = ImageDraw.Draw(limage)
            next_symbol_spacing = 0
            skip_times = 0
            for symbol in range(len(line)):
                if skip_times > 0:
                    skip_times -= 1
                    continue
                if line[symbol] == '/' and line[symbol+1] == 'b':
                    skip_times +=1
                    current_font = font_bold
                    continue
                if line[symbol] == '/' and line[symbol+1] == '/' and line[symbol+2] == 'b':
                    skip_times +=2
                    current_font = font
                    continue
                
                ldraw.text((next_symbol_spacing, 0), line[symbol], font=current_font, fill='black')

                wSize = current_font.getlength(line[symbol])
                next_symbol_spacing += wSize
            image.paste(limage, (int((W-next_symbol_spacing)/2), next_line_spacing+HEIGHT_OFFSET), mask=limage)
            next_line_spacing += LINE_SPACING_INC
            
        
        bg_w, bg_h = descrtiption_banner.size
        img_w, img_h = image.size        
        t_offset = ((bg_w - img_w) // 2, ((bg_h - img_h) // 2))

        descrtiption_banner.paste(image, t_offset, mask=image)

        return descrtiption_banner

    def generate_rarity_gem(self, rarity: Rarity = Rarity.NONE) -> Image:
        if rarity == Rarity.COMMON:
            path = self.RESOURCE_GEM_COMMON_PATH
        elif rarity == Rarity.RARE:
            path = self.RESOURCE_GEM_RARE_PATH
        elif rarity == Rarity.EPIC:
            path = self.RESOURCE_GEM_EPIC_PATH
        elif rarity == Rarity.LEGENDARY:
            path = self.RESOURCE_GEM_LEGENDARY_PATH
        elif rarity == Rarity.NONE:
            return Image.new('RGBA', (0,0))

        return self.ImageFromRes(path, 'r').convert('RGBA')

    def generate_legendary_dragon(self):
        return self.ImageFromRes(self.RESOURCE_LEGENDARY_DRAGON_PATH, 'r').convert('RGBA')

    def generate_managem(self, manacost: int = None) -> Image:
        managem = self.ImageFromRes(self.RESOURCE_MANATEXTURE_PATH, 'r').convert('RGBA')

        if manacost is None:
            return managem
        
        draw = ImageDraw.Draw(managem)
        
        if manacost is not None and manacost < 100 and manacost > -1:
            font= self.ImageFontFromRes(self.RESOURCE_FONT_PATH, 200)
            w, h = 35, -45
            if manacost >= 10:
                w, h = -8, -35
                font= self.ImageFontFromRes(self.RESOURCE_FONT_PATH, 180)
            for x in range(-3, 4):
                for y in range(-3, 4):
                    draw.text((w+x, h+y), str(manacost), font=font, fill='black')
            draw.text((w, h), str(manacost), font=font, fill='white')

        return managem

    def generate_attack(self, attack: int = None) -> Image:
        attack_gem = self.ImageFromRes(self.RESOURCE_ATTACKTEXTURE_PATH, 'r').convert('RGBA')
        
        draw = ImageDraw.Draw(attack_gem)
        
        if attack is not None and attack < 100:
            font= self.ImageFontFromRes(self.RESOURCE_FONT_PATH, 170)
            w, h = 90, 20
            if attack >= 10 or attack < 0:
                w, h = 55, 30
                font= self.ImageFontFromRes(self.RESOURCE_FONT_PATH, 150)
            for x in range(-3, 4):
                for y in range(-3, 4):
                    draw.text((w+x, h+y), str(attack), font=font, fill='black')
            draw.text((w, h), str(attack), font=font, fill='white')

        return attack_gem

    def generate_health(self, health: int = None) -> Image:
        health_gem = self.ImageFromRes(self.RESOURCE_HEALTHTEXTURE_PATH, 'r').convert('RGBA')
        
        draw = ImageDraw.Draw(health_gem)
        
        if health is not None and health < 100:
            font= self.ImageFontFromRes(self.RESOURCE_FONT_PATH, 170)
            w, h = 55, 10
            if health >= 10 or health < 0:
                w, h = 21, 20
                font= self.ImageFontFromRes(self.RESOURCE_FONT_PATH, 150)
            for x in range(-3, 4):
                for y in range(-3, 4):
                    draw.text((w+x, h+y), str(health), font=font, fill='black')
            draw.text((w, h), str(health), font=font, fill='white')

        return health_gem
    
    def generate_tribe(self, text: str = None) -> Image:
        tribe = self.ImageFromRes(self.RESOURCE_TRIBE_PLAQUE_PATH, 'r').convert('RGBA')

        if not text:
            return tribe
        if len(text) > 10:
            return tribe

        draw = ImageDraw.Draw(tribe)

        font = self.ImageFontFromRes(self.RESOURCE_FONT_PATH, 44)
        if Validate.has_cyrillic(text):
            font = self.ImageFontFromRes(self.RESOURCE_FONT_C_PATH, 44)

        w, h = 245 + 13.5, 32
        w-=len(text) * 13.5
        for x in range(-2, 3):
            for y in range(-2, 3):
                draw.text((w+x, h+y), text, font=font, fill='black')
        draw.text((w, h), text, font=font, fill='white')

        return tribe

    def combine_images(self, background, image, t_offset=None) -> Image:
        if isinstance(background, str):
            background = self.ImageFromRes(background).convert('RGBA')
        if isinstance(image, str):
            image = self.ImageFromRes(image).convert('RGBA')

        if not t_offset:
            bg_w, bg_h = background.size
            img_w, img_h = image.size
            t_offset = ((bg_w - img_w) // 2, ((bg_h - img_h) // 2))

        background.paste(image, t_offset, mask=image)
        return background
    
    def text_wrap(self, text, font, max_width, strip=False) -> list:
        lines = []
        
        # If the text width is smaller than the image width, then no need to split
        # just add it to the line list and return
        if font.getlength(text)  <= max_width:
            lines.append(text)
        else:
            #split the line by spaces to get words
            words = text.split(' ')
            i = 0
            # append every word to a line while its width is shorter than the image width
            while i < len(words):
                line = ''
                while i < len(words) and font.getlength(line + words[i]) <= max_width:
                    line = line + words[i]+ " "
                    i += 1
                if not line:
                    line = words[i]
                    i += 1
                lines.append(line)

        # Support \n newline
        # Only one per line TODO: multiple per line
        try:
            for i in range(len(lines)):
                if '\n' in lines[i]:
                    first_half, second_half = lines.pop(i).split('\n')
                    lines.insert(i, second_half.strip())
                    lines.insert(i, first_half.strip())
        except ValueError:
            pass
        
        lines = list(filter(None, lines))
        if strip:
            lines = list(map(str.strip, lines))

        return lines

    def get_text_size_for_12px_font(self, font_path: str, text: str) -> int:
        font = self.ImageFontFromRes(font_path, 12)
        size = font.getlength(text)
        return size
        
    def get_text_adjust_params(self, text_size_px: int) -> Tuple[int,int,int]:
        return  int(self.get_font_size(text_size_px)),    \
                int(self.get_curve_degree(text_size_px)), \
                int(self.get_offset(text_size_px))

    def get_font_size(self, text_size_px: int) -> float:
        x = text_size_px
        return -0.001586925873221*(x**2)+0.081728927577078*x+68.110135256781558

    def get_curve_degree(self, text_size_px: int) -> float:
        x = text_size_px
        return -0.000010731420018*(x**3)+0.002294332290798*(x**2)+0.006577248376604*x+19.527607034700898

    def get_offset(self, text_size_px: int) -> float:
        x = text_size_px
        #return 0.000004841197185*(x**3)+0.000805895575798*(x**2)-0.490495518803842*x+110.555105881367560
        return 0.000000000000000*(x**8)+0.000000000000000*(x**7)+0.000000000310011*(x**6) \
        -0.000000170873051*(x**5)+0.000036060789004*(x**4)-0.003637973111197*(x**3) \
        +0.180793592168535*(x**2)-4.461212339169927*x+140.206273116060634


    def ImageFromRes(self, path: str, mode = 'r') -> Image:
        file = QFile(path)
        if not file.open(QFile.ReadOnly):
            raise GenerationError("Unable to open resource file")

        data = file.readAll()
        file.close()

        return Image.open(BytesIO(data), mode)

    def ImageFontFromRes(self, path: str, size: int) -> ImageFont:
        file = QFile(path)
        if not file.open(QFile.ReadOnly):
            raise GenerationError("Unable to open resource file")

        data = file.readAll()
        file.close()

        return ImageFont.truetype(BytesIO(data), size)

