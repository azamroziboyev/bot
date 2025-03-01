import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from recept import convert_narxi, save_table_as_image, save_real_time_inputs_to_excel
import pandas as pd

# Initialize the bot and dispatcher
bot = Bot(token="7614309818:AAE6QqlXGdFYcinUBkD3qBtL8NWYsixDYhU")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Initialize an empty list to store the data
data = []

# Command to start the bot
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Welcome! Please enter the Xaridor name:")

# Handler for Xaridor input
@dp.message_handler()
async def handle_xaridor(message: types.Message):
    xaridor = message.text
    await message.answer(f"Xaridor set to: {xaridor}\n\nNow, enter 'Nomi' (or type /stop to finish):")
    await message.answer("Enter Nomi:")
    dp.current_state().update_data(xaridor=xaridor)

# Handler for Nomi input
@dp.message_handler()
async def handle_nomi(message: types.Message):
    nomi = message.text
    if nomi.lower() == '/stop':
        await finish(message)
        return
    await message.answer(f"Nomi: {nomi}\n\nNow, enter Narxi:")
    dp.current_state().update_data(nomi=nomi)

# Handler for Narxi input
@dp.message_handler()
async def handle_narxi(message: types.Message):
    narxi_input = message.text
    narxi = convert_narxi(narxi_input)
    if narxi is None:
        await message.answer("Invalid Narxi! Please enter a valid number.")
        return
    await message.answer(f"Narxi: {narxi}\n\nNow, enter Soni:")
    dp.current_state().update_data(narxi=narxi)

# Handler for Soni input
@dp.message_handler()
async def handle_soni(message: types.Message):
    try:
        soni = int(message.text.replace(" ", ""))
    except ValueError:
        await message.answer("Invalid Soni! Please enter a numeric value.")
        return
    
    # Get data from the state
    state_data = dp.current_state().get_data()
    nomi = state_data.get('nomi')
    narxi = state_data.get('narxi')
    xaridor = state_data.get('xaridor')
    
    # Append the input values as a new row in the data list
    data.append([nomi, narxi, soni])
    
    # Save real-time inputs to another Excel file
    excel_filename = save_real_time_inputs_to_excel(data, xaridor)
    await message.answer(f"Data saved to {excel_filename}.\n\nEnter another 'Nomi' (or type /stop to finish):")
    await message.answer("Enter Nomi:")

# Command to finish and generate the final image
@dp.message_handler(commands=['stop'])
async def finish(message: types.Message):
    if not data:
        await message.answer("No data entered.")
        return
    
    # Get Xaridor from the state
    state_data = dp.current_state().get_data()
    xaridor = state_data.get('xaridor')
    
    # Create the DataFrame and save the table as an image
    df = pd.DataFrame(data, columns=["Nomi", "Narxi", "Soni"])
    image_filename = save_table_as_image(df, xaridor)
    
    # Send the image to the user
    with open(image_filename, 'rb') as photo:
        await message.answer_photo(photo, caption="Here is your final table:")
    
    # Clear the data for the next session
    data.clear()

# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)