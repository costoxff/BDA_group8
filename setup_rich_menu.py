from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    RichMenuRequest,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    MessageAction,
    PostbackAction,
    URIAction
)
import os
import sys
import requests

from utils.env import LINE_CHANNEL_ACCESS_TOKEN


def upload_rich_menu_image(rich_menu_id, image_path):
    url = f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content'
    
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'image/png'
    }
    
    with open(image_path, 'rb') as f:
        response = requests.post(url, headers=headers, data=f.read())
    
    if response.status_code == 200:
        return True
    else:
        print(f" Upload failed: {response.status_code}")
        print(f" Response: {response.text}")
        return False


def create_rich_menu():
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        
        rich_menu_request = RichMenuRequest(
            size=RichMenuSize(width=2500, height=843),
            selected=True,
            name="main rich menu",
            chat_bar_text="選單",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=834, height=843),
                    action=PostbackAction(
                        label='諮詢專線',
                        data='call'
                    )
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                    action=URIAction(label='動畫影片', uri="https://youtu.be/2Eh79wr7aSw")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1667, y=0, width=833, height=843),
                    action=PostbackAction(label='問答總結', data='send')
                )
            ]
        )
        
        try:
            response = messaging_api.create_rich_menu(rich_menu_request=rich_menu_request)
            rich_menu_id = response.rich_menu_id
            
            image_path = 'rich_menu_image.png'
            if not os.path.exists(image_path):
                print(f"{image_path} is not exist")
                messaging_api.delete_rich_menu(rich_menu_id=rich_menu_id)
                return
            
            if not upload_rich_menu_image(rich_menu_id, image_path):
                print("Upload failed, delete the Rich Menu")
                messaging_api.delete_rich_menu(rich_menu_id=rich_menu_id)
                return
            
            messaging_api.set_default_rich_menu(rich_menu_id=rich_menu_id)
            
            return rich_menu_id
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return


def list_rich_menus():
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        
        try:
            response = messaging_api.get_rich_menu_list()
            rich_menus = response.richmenus
            
            if not rich_menus:
                print("Rich Menu")
                return
            
            print(f"Find {len(rich_menus)} Rich Menu:\n")
            for menu in rich_menus:
                print(f"  * name: {menu.name}")
                print(f"    ID: {menu.rich_menu_id}")
                print(f"    size: {menu.size.width}x{menu.size.height}")
                print(f"    font: {menu.chat_bar_text}")
                print(f"    num areas: {len(menu.areas)}")
                print()
                
        except Exception as e:
            print(f"Error occur when listing Rich Menu: {e}")


def delete_rich_menu(rich_menu_id):
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        
        try:
            messaging_api.delete_rich_menu(rich_menu_id=rich_menu_id)
            print(f"Rich Menu: {rich_menu_id} is deleted")
        except Exception as e:
            print(f"Error occur when deleting Rich Menu: {e}")


def delete_all_rich_menus():
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        
        try:
            response = messaging_api.get_rich_menu_list()
            rich_menus = response.richmenus
            
            if not rich_menus:
                return
            
            for menu in rich_menus:
                messaging_api.delete_rich_menu(rich_menu_id=menu.rich_menu_id)
                print(f"Delete: {menu.name} ({menu.rich_menu_id})")
            
        except Exception as e:
            print(f" Error occur when deleting Rich Menu: {e}")


def create_test_image():
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (2500, 843), color="#000000")
    draw = ImageDraw.Draw(img)
    
    colors = ['#FFA07A', '#4ECDC4', '#45B7D1']
    
    areas = [
        (0, 0, 833, 843, colors[0], '諮詢專線'),
        (833, 0, 1667, 843, colors[1], '動畫影片'),
        (1667, 0, 2500, 843, colors[2], '問答總結'),
    ]
    
    for x1, y1, x2, y2, color, text in areas:
        draw.rectangle([x1, y1, x2, y2], fill=color)
        draw.rectangle([x1, y1, x2, y2], outline='white', width=2)

        try:
            font = ImageFont.truetype("NotoSansTC-Medium.ttf", 150)
        except:
            font = ImageFont.load_default()


        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x1 + (x2 - x1 - text_width) // 2
        text_y = y1 + (y2 - y1 - text_height) // 2

        text_y -= 30

        shadow_offset = 3

        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, fill=(0, 0, 0, 100), font=font)
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        
        
    img.save('rich_menu_image.png')
    print("test images has been created: rich_menu_image.png")
    print(f"   size: 2500x843 pixels")


def print_usage():
    print("""
usage:
  uv run setup_rich_menu.py [arguments]

arguments list:
  (no arg)     create new Rich Menu
  create       create new Rich Menu
  list         list all Rich Menu
  delete       delete all Rich Menu
  test-image   create test image
  help         display usage

example:
  uv run setup_rich_menu.py                  # create Rich Menu
  uv run setup_rich_menu.py test-image       # create test image first
  uv run setup_rich_menu.py list             # list all exist Rich Menu
  uv run setup_rich_menu.py delete           # remove all exist Rich Menu
  
note:
  * Need rich_menu_image.png (2500 x 1686 or 2500 x 843)
    """)


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'create'
    
    if command == 'help':
        print_usage()
    elif command == 'list':
        list_rich_menus()
    elif command == 'delete':
        confirm = input("Remove all Rich Menu (yes/no): ")
        if confirm.lower() == 'yes':
            delete_all_rich_menus()
        else:
            print("cancel")
    elif command == 'test-image':
        create_test_image()
    elif command == 'create':
        create_rich_menu()
    else:
        print(f"unknow command: {command}")
        print_usage()