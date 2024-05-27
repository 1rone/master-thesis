from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox
from TokensCollectors.AdColonyToken import AdColonyToken
from TokensCollectors.DTExchangeToken import DTExchangeToken
from TokensCollectors.MyTargetToken import MyTargetToken
from AdServices.BlockedCategories.UnityCategoriesName import UnityBlockedCategories
from TokensCollectors.UnityToken import UnityToken
from TokensCollectors.YandexToken import YandexToken
from TokensCollectors.InmobiToken import InmobiToken
from Convertors.FrontToInmobiConvertor import FrontToInmobiConvertor
from Convertors.FrontToUnityConvertor import FrontToUnityConvertor
from Convertors.FrontToAdColonyConvertor import FrontToAdcolonyConvertor
from Convertors.FrontToPangleConvertor import FrontToPangleConvertor
from Convertors.AdServiceToTokenConvertor import AdServiceToTokenConvertor
from Convertors.InputToChartBoostConvertor import InputToChartBoostConvertor
from backend import unit_auto_creating
from Enums.Enums import AdServices, Mediators, InmobiConsentOfAgeId, ChartBoostOrientations, \
    IronSourceAdServicesAdditional


def renew_all() -> str:
    # if current_user.value == UserNames.Oleh.value:
    #     tokens = [UnityToken(kids=True),
    #               UnityToken(kids=False),
    #               YandexToken(),
    #               MyTargetToken(),
    #               TapJoyToken(),
    #               InmobiToken(kids=True),
    #               InmobiToken(kids=False),
    #               AdColonyToken(),
    #               DTExchangeToken()]
    #
    #     threads = []
    #     results = []
    #
    #     for token in tokens:
    #         thread = threading.Thread(target=send_new_token, args=(token, results))
    #         threads.append(thread)
    #         thread.start()
    #
    #     for thread in threads:
    #         thread.join()
    #
    #     return '\n'.join(results)
    # else:
    return f'{UnityToken(kids=True).send_new_token()}' \
           f'\n{UnityToken(kids=False).send_new_token()}' \
           f'\n{YandexToken().send_new_token()}' \
           f'\n{MyTargetToken().send_new_token()}' \
           f'\n{InmobiToken(kids=True).send_new_token()}' \
           f'\n{InmobiToken(kids=False).send_new_token()}' \
           f'\n{AdColonyToken().send_new_token()}' \
           f'\n{DTExchangeToken().send_new_token()}'


def send_new_token(token, results):
    result = token.send_new_token()
    results.append(result)


def get_pangle_app_cat_id(big_cat_name, small_cat_name) -> int:
    answer = {"Business-Notebook and Net Storage": 120102, "Business-Productivity": 120104,
              "Business-Others": 120106, "Travel and Transport-Maps and Navigation": 120201,
              "Travel and Transport-Public Transport": 120202, "Travel and Transport-Shared Transportation": 120203,
              "Travel and Transport-Travel Service": 120211, "Travel and Transport-Car Owner Services": 120212,
              "Travel and Transport-Others": 120218,
              "Shopping/E-commerce-Product Review and Price Comparison": 120301,
              "Shopping/E-commerce-Ecommerce Platform Services": 120302,
              "Shopping/E-commerce-Second-hand Goods": 120303, "Shopping/E-commerce-Ecommerce": 120305,
              "Shopping/E-commerce-Others": 120306, "Health & Fitness-Health Management": 120402,
              "Health & Fitness-Beauty Products": 120403, "Health & Fitness-Aesthetic Medicine": 120404,
              "Health & Fitness-Workout Tracking": 120405, "Health & Fitness-Medical Services": 120407,
              "Health & Fitness-Hospital Queue Service": 120408, "Health & Fitness-Woman's Health": 120409,
              "Health & Fitness-Others": 120413, "Education-K12": 120501, "Education-Dictionaries": 120502,
              "Education-Higher Education": 120503, "Education-Education Tools": 120504,
              "Education-Preschool Education": 120505, "Education-Language Learning": 120506,
              "Education-Professional Education": 120507, "Education-Others": 120508, "Finance-Insurance": 120602,
              "Finance-Stock Trading": 120603, "Finance-Banking": 120606, "Finance-Others": 120613,
              "Social Networking-Interactive Dating": 120701, "Social Networking-Instant Messaging": 120702,
              "Social Networking-Community Forum": 120703, "Social Networking-Others": 120708,
              "Lifestyle-Local Guides": 120803, "Lifestyle-Recipes": 120809, "Lifestyle-Employment": 120810,
              "Lifestyle-Others": 120813, "Videos-Horizontal Version of Short Video": 120903,
              "Videos-Video Players": 120905, "Videos-Video Editing Tools": 120906,
              "Videos-Live Broadcasting": 120908, "Videos-Long-form Video": 120909, "Videos-Others": 120910,
              "Videos-Vertical Layout Short Video": 120911, "Photo-Photography": 121001,
              "Photo-Image Sharing": 121002, "Photo-Photo Editing": 121003, "Photo-Photo Albums": 121004,
              "Photo-Others": 121005, "Utilities-Emails": 121101, "Utilities-Communication Aids": 121102,
              "Utilities-Texting and Calling": 121104, "Utilities-System Widgets": 121106,
              "Utilities-Weather": 121111, "Utilities-Calendar": 121113, "Utilities-Horoscopes": 121114,
              "Utilities-WiFi": 121116, "Utilities-Browser": 121118, "Utilities-Keyboards": 121119,
              "Utilities-File Management": 121122, "Utilities-Cleaner and Booster": 121123,
              "Utilities-App Store": 121124, "Utilities-Wallpaper": 121127, "Utilities-Ringtones": 121128,
              "Utilities-Others": 121133, "Music-Karaoke": 121201, "Music-Music Players": 121203,
              "Music-Musical Instruments": 121204, "Music-Music Recognition": 121205, "Music-Music": 121206,
              "Music-Others": 121207, "Music-Audiobook": 121208, "Games-Game Center": 121315,
              "Games-Role Playing Game": 121319, "Games-Hardcore-Strategy Game": 121320,
              "Games-Social Game": 121322, "Games-Shooting Game": 121323, "Games-Racing Game": 121324,
              "Games-Sports Game": 121325, "Games-Simulation Game": 121326, "Games-Action Game": 121327,
              "Games-Strategy Tower Defense Game": 121328, "Games-Merge Game": 121329, "Games-Match 3": 121330,
              "Games-Idle Game": 121331, "Games-Quiz Game": 121332, "Games-Puzzle Game": 121333,
              "Games-Music Game": 121334, "Games-Arcade Runner": 121335, "Games-Casual-Card Game": 121336,
              "Games-Word": 121337, "Games-Female Orientated": 121338, "Games-MOBA": 121339,
              "Games-Chinese Fantasy": 121340, "Games-Adventure": 121341, "Games-Sandbox": 121342,
              "Games-Card": 121343, "Games-Others": 121344, "Reading-Animation & Manga": 121402,
              "Reading-Online Reading": 121405, "Reading-Others": 121406,
              "Government-Government Services": 121501, "Government-Others": 121502,
              "Smart Devices-Smart Wearables": 121601, "Smart Devices-Smart Home": 121602,
              "Smart Devices-Others": 121606, "News-Sports News": 121704, "News-Integrated News": 121707,
              "News-Others": 121708, "News-Official Government Info": 121709, "News-Information Portal": 121710,
              "Others-Others": 121801, "Tech Finance-Consumer Finance": 121901,
              "Tech Finance-Virtual Currencies": 121902, "Tech Finance-Lotteries": 121903,
              "Tech Finance-Payment": 121904, "Tech Finance-Integrated Financial Services": 121905,
              "Tech Finance-Get Paid To": 121906, "Tech Finance-Peer to Peer Finanace": 121907,
              "Tech Finance-Bookkeeping & Management": 121908, "Tech Finance-Loans": 121909,
              "Tech Finance-Others": 121910, "Infrastructure-Energy": 122001, "Infrastructure-Shipping": 122002,
              "Infrastructure-ISP Services": 122003, "Infrastructure-Transportation": 122004,
              "Infrastructure-Others": 122005, "Media Outlets-Newspaper": 122101, "Media Outlets-CCTV": 122102,
              "Media Outlets-Publishing": 122103, "Media Outlets-Broadcasting": 122104,
              "Media Outlets-Others": 122105}
    return answer[f'{big_cat_name}-{small_cat_name}']


class App:
    def __init__(self):
        self.root = Tk()
        Label(self.root, text='Select AdService and Mediation').grid(row=0, sticky=W)
        self.ad_selector_variable = StringVar()
        self.mediation_variable = StringVar()
        self.ad_selector = Combobox(self.root,
                                    state='readonly',
                                    values=[i.value for i in AdServices],
                                    textvariable=self.ad_selector_variable)
        self.ad_selector.current(0)
        self.ad_selector.grid(row=1, sticky=W)
        mediation_selector = Combobox(self.root,
                                      state='readonly',
                                      values=[i.value for i in Mediators],
                                      textvariable=self.mediation_variable)
        mediation_selector.current(0)
        mediation_selector.grid(row=2, sticky=W)
        mediation_selector.bind("<<ComboboxSelected>>", self.__mediation_ad_services)
        Button(self.root, text='Start', command=self.ad_service_select).grid(row=4, sticky=W)
        self.root.mainloop()

    def __mediation_ad_services(self, event=None):
        def max_mediation_services():
            self.ad_selector = Combobox(self.root,
                                        state='readonly',
                                        values=[
                                            AdServices.AdColony.value,
                                            AdServices.InmobiAdults.value,
                                            AdServices.InmobiKids.value,
                                            AdServices.MaxAdults.value,
                                            AdServices.MaxKids.value,
                                            AdServices.Mintegral.value,
                                            AdServices.MyTargetAdults.value,
                                            AdServices.MyTargetKids.value,
                                            AdServices.Pangle.value,
                                            AdServices.VungleAdults.value,
                                            AdServices.VungleKids.value,
                                        ],
                                        textvariable=self.ad_selector_variable)
            self.ad_selector.current(0)
            self.ad_selector.grid(row=1, sticky=W)

        def cas_mediation_services():
            self.ad_selector = Combobox(self.root,
                                        state='readonly',
                                        values=[i.value for i in AdServices],
                                        textvariable=self.ad_selector_variable)
            self.ad_selector.current(0)
            self.ad_selector.grid(row=1, sticky=W)

        def is_mediation_services():
            self.ad_selector = Combobox(self.root,
                                        state='readonly',
                                        values=[
                                            AdServices.AdColony.value,
                                            IronSourceAdServicesAdditional.AdMob.value,
                                            AdServices.InmobiAdults.value,
                                            AdServices.InmobiKids.value,
                                            AdServices.IronSourceAdults.value,
                                            AdServices.IronSourceKids.value,
                                            AdServices.Pangle.value,
                                            AdServices.UnityAdults.value,
                                            AdServices.UnityKids.value,
                                            AdServices.VungleAdults.value,
                                            AdServices.VungleKids.value,
                                        ],
                                        textvariable=self.ad_selector_variable)
            self.ad_selector.current(0)
            self.ad_selector.grid(row=1, sticky=W)

        match self.mediation_variable.get():
            case Mediators.MAX.value:
                max_mediation_services()
            case Mediators.CAS.value:
                cas_mediation_services()
            case Mediators.IS.value:
                is_mediation_services()
            case _:
                cas_mediation_services()

    def ad_service_select(self):
        new_window = Toplevel(master=self.root)
        new_window.title(self.ad_selector_variable.get() + '' + self.mediation_variable.get())
        ad_label = Label(master=new_window, text=self.ad_selector_variable.get() + '' + self.mediation_variable.get(),
                         fg='red')
        ad_label.grid(row=0, sticky=W)
        Label(new_window, text='Bundle').grid(row=1, sticky=W)
        bundle_entry = Entry(new_window)
        bundle_entry.grid(row=2, sticky=W)

        ad_service = self.ad_selector_variable.get()
        mediator = self.mediation_variable.get()

        def activate_btn(event=None):
            btn['state'] = NORMAL

        match ad_service:
            case AdServices.UnityKids.value | AdServices.UnityAdults.value:

                ubc = UnityBlockedCategories()
                Label(new_window, text='Виберіть категорії реклами які відключаємо').grid(row=5, column=0, sticky=W)
                ad_cat_of = StringVar()
                Radiobutton(master=new_window,
                            text='Toddlers: ' + ','.join(ubc.get_toddlers()),
                            value='Toddlers',
                            variable=ad_cat_of,
                            command=activate_btn).grid(row=6, sticky=W)
                Radiobutton(master=new_window,
                            text='Kids: ' + ','.join(ubc.get_kids()),
                            value='Kids',
                            variable=ad_cat_of,
                            command=activate_btn).grid(row=7, sticky=W)
                Radiobutton(master=new_window,
                            text='Teens: ' + ','.join(ubc.get_teens()),
                            value='Teens',
                            variable=ad_cat_of,
                            command=activate_btn).grid(row=8, sticky=W)
                Radiobutton(master=new_window,
                            text='Mature: ' + ','.join(ubc.get_mature()),
                            value='Mature',
                            variable=ad_cat_of,
                            command=activate_btn).grid(row=9, sticky=W)
                Radiobutton(master=new_window,
                            text='Adults: ' + ','.join(ubc.get_adults()),
                            value='Adults',
                            variable=ad_cat_of,
                            command=activate_btn).grid(row=10, sticky=W)

                age_selector_variable = StringVar()
                age_selector = Combobox(master=new_window,
                                        state='readonly',
                                        values=['5+', '9+', '13+', '17+', '21+'],
                                        textvariable=age_selector_variable)
                age_selector.current(0)
                Label(master=new_window, text='Вибір вікової категорії').grid(row=11, sticky=W)
                age_selector.grid(row=12, sticky=W)
                btn = Button(master=new_window,
                             text='Запуск',
                             command=lambda: messagebox.showinfo(
                                 message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                            mediator=mediator,
                                                            ad_service=ad_service,
                                                            age=age_selector_variable.get()[:-1],
                                                            categories=FrontToUnityConvertor.get_categories(
                                                                ad_cat_of.get()))),
                             state=DISABLED)
                btn.grid(
                    row=13, sticky=W)

            case IronSourceAdServicesAdditional.AdMob.value:

                coppa_var = BooleanVar()
                Checkbutton(master=new_window,
                            text='COPPA',
                            variable=coppa_var,
                            onvalue=1,
                            offvalue=0).grid(row=6, sticky=W)

                Button(master=new_window,
                       text='Запуск',
                       command=lambda: messagebox.showinfo(
                           message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                      mediator=mediator,
                                                      ad_service=ad_service,
                                                      coppa=int(coppa_var.get())))).grid(
                    row=12, sticky=W)

            case AdServices.Mintegral.value:

                coppa_var = BooleanVar()
                mature_var = BooleanVar()
                Checkbutton(master=new_window,
                            text='COPPA',
                            variable=coppa_var,
                            onvalue=1,
                            offvalue=0).grid(row=6, sticky=W)
                Checkbutton(master=new_window,
                            text='Mature',
                            variable=mature_var,
                            onvalue=1,
                            offvalue=0).grid(row=7, sticky=W)
                Label(master=new_window,
                      text='Direction Of Fullscreen Video').grid(row=8, sticky=W)
                orientation_var = StringVar()
                orientation_selector = Combobox(master=new_window,
                                                state='readonly',
                                                values=['both', 'portrait', 'landscape'],
                                                textvariable=orientation_var)
                orientation_selector.current(0)
                orientation_selector.grid(row=9, sticky=W)
                Button(master=new_window,
                       text='Запуск',
                       command=lambda: messagebox.showinfo(
                           message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                      mediator=mediator,
                                                      ad_service=ad_service,
                                                      coppa=int(coppa_var.get()),
                                                      mature=int(mature_var.get()),
                                                      orientation=orientation_var.get()))).grid(
                    row=12, sticky=W)

            case AdServices.Pangle.value:

                Label(master=new_window, text='Child Protection').grid(row=5, sticky=W)
                coppa_var = StringVar()
                coppa_selector = Combobox(master=new_window,
                                          state='readonly',
                                          values=['For age 13+', 'For Age 12 or under', 'Client-side Configuration'],
                                          textvariable=coppa_var)
                coppa_selector.current(newindex=2)
                coppa_selector.grid(row=6, sticky=W)
                Label(master=new_window, text='Blocking').grid(row=7, sticky=W)
                block_var = StringVar()
                block_selector = Combobox(master=new_window,
                                          state='readonly',
                                          values=['Children',
                                                  'Teens up to 17+',
                                                  'Mature: азартных игр, алкоголя, знакомств, политики',
                                                  'Adult'],
                                          textvariable=block_var)
                block_selector.current(newindex=3)
                block_selector.grid(row=8, sticky=W)
                Label(master=new_window, text='Orientation').grid(row=9, sticky=W)
                orientation_var = StringVar()
                orientation_selector = Combobox(master=new_window,
                                                state='readonly',
                                                values=['horizontal', 'vertical'],
                                                textvariable=orientation_var)
                orientation_selector.current(0)
                orientation_selector.grid(row=10, sticky=W)
                Label(master=new_window,
                      text='Select app category (1/2)').grid(row=11, sticky=W)

                def change_cat_selector(event=None):
                    if big_cat.get() == 'Games':
                        values = ['Game Center', 'Role Playing Game', 'Hardcore-Strategy Game', 'Social Game',
                                  'Shooting Game',
                                  'Racing Game', 'Sports Game', 'Simulation Game', 'Action Game',
                                  'Strategy Tower Defense Game',
                                  'Merge Game', 'Match 3', 'Idle Game', 'Quiz Game', 'Puzzle Game', 'Music Game',
                                  'Arcade Runner',
                                  'Casual-Card Game', 'Word', 'Female Orientated', 'MOBA', 'Chinese Fantasy',
                                  'Adventure',
                                  'Sandbox', 'Card', 'Others']
                    elif big_cat.get() == 'Business':
                        values = ['Notebook and Net Storage', 'Productivity', 'Others']
                    elif big_cat.get() == 'Travel and Transport':
                        values = ['Maps and Navigation', 'Public Transport', 'Shared Transportation', 'Travel Service',
                                  'Car Owner Services', 'Others']
                    elif big_cat.get() == 'Shopping/E-commerce':
                        values = ['Product Review and Price Comparison', 'Ecommerce Platform Services',
                                  'Second-hand Goods',
                                  'Ecommerce', 'Others']
                    elif big_cat.get() == 'Health & Fitness':
                        values = ['Health Management', 'Beauty Products', 'Aesthetic Medicine', 'Workout Tracking',
                                  'Medical Services', 'Hospital Queue Service', 'Woman\'s Health', 'Others']
                    elif big_cat.get() == 'Education':
                        values = ['K12', 'Dictionaries', 'Higher Education', 'Education Tools', 'Preschool Education',
                                  'Language Learning', 'Professional Education', 'Others']
                    elif big_cat.get() == 'Finance':
                        values = ['Insurance', 'Stock Trading', 'Banking', 'Others']
                    elif big_cat.get() == 'Social Networking':
                        values = ['Interactive Dating', 'Instant Messaging', 'Community Forum', 'Others']
                    elif big_cat.get() == 'Lifestyle':
                        values = ['Local Guides', 'Recipes', 'Employment', 'Others']
                    elif big_cat.get() == 'Videos':
                        values = ['Horizontal Version of Short Video', 'Video Players', 'Video Editing Tools',
                                  'Live Broadcasting', 'Long-form Video', 'Vertical Layout Short Video', 'Others']
                    elif big_cat.get() == 'Photo':
                        values = ['Photography', 'Image Sharing', 'Photo Editing', 'Photo Albums', 'Others']
                    elif big_cat.get() == 'Utilities':
                        values = ['Emails', 'Communication Aids', 'Texting and Calling', 'System Widgets', 'Weather',
                                  'Calendar', 'Horoscopes', 'WiFi', 'Browser', 'Keyboards', 'File Management',
                                  'Cleaner and Booster', 'App Store', 'Wallpaper', 'Ringtones', 'Others']
                    elif big_cat.get() == 'Music':
                        values = ['Karaoke', 'Music Players', 'Musical Instruments', 'Music Recognition', 'Music',
                                  'Audiobook',
                                  'Others']
                    elif big_cat.get() == 'Reading':
                        values = ['Animation & Manga', 'Online Reading', 'Others']
                    elif big_cat.get() == 'Government':
                        values = ['Government Services', 'Others']
                    elif big_cat.get() == 'Smart Devices':
                        values = ['Smart Wearables', 'Smart Home', 'Others']
                    elif big_cat.get() == 'News':
                        values = ['Sports News', 'Integrated News', 'Official Government Info', 'Information Portal',
                                  'Others']
                    elif big_cat.get() == 'Tech Finance':
                        values = ['Consumer Finance', 'Virtual Currencies', 'Lotteries', 'Payment',
                                  'Integrated Financial Services', 'Get Paid To', 'Peer to Peer Finanace',
                                  'Bookkeeping & Management', 'Loans', 'Others']
                    elif big_cat.get() == 'Infrastructure':
                        values = ['Energy', 'Shipping', 'ISP Services', 'Transportation', 'Others']
                    elif big_cat.get() == 'Media Outlets':
                        values = ['Newspaper', 'CCTV', 'Publishing', 'Broadcasting', 'Others']
                    elif big_cat.get() == 'Others':
                        values = ['Others']
                    else:
                        raise Exception('wrong category pangle')

                    categories = Combobox(master=new_window,
                                          state='readonly',
                                          values=values,
                                          textvariable=cat_var)
                    categories.current(0)
                    Label(master=new_window,
                          text='Select app category (2/2)').grid(row=13, sticky=W)
                    categories.grid(row=14, sticky=W)

                cat_var = StringVar()
                big_cat_var = StringVar()
                big_cat = Combobox(master=new_window,
                                   state='readonly',
                                   values=['Games', 'Business', 'Travel and Transport', 'Shopping/E-commerce',
                                           'Health & Fitness', 'Education', 'Finance', 'Social Networking', 'Lifestyle',
                                           'Videos', 'Photo', 'Utilities', 'Music', 'Reading', 'Government',
                                           'Smart Devices', 'News', 'Tech Finance', 'Infrastructure', 'Media Outlets',
                                           'Others'],
                                   textvariable=big_cat_var)
                big_cat.grid(row=12, sticky=W)
                big_cat.current(0)
                change_cat_selector()
                big_cat.bind("<<ComboboxSelected>>", change_cat_selector)
                Button(master=new_window,
                       text='Start',
                       command=lambda: messagebox.showinfo(
                           message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                      mediator=mediator,
                                                      ad_service=ad_service,
                                                      app_category=get_pangle_app_cat_id(
                                                          big_cat_name=big_cat_var.get(),
                                                          small_cat_name=cat_var.get()),
                                                      coppa=FrontToPangleConvertor.get_coppa_id(name=coppa_var.get()),
                                                      category_id=FrontToPangleConvertor.get_block_cat_id(
                                                          name=block_var.get()),
                                                      orientation=orientation_var.get()
                                                      )
                       )).grid(row=18, sticky=W)

            case AdServices.IronSourceKids.value | AdServices.IronSourceAdults.value:

                Label(master=new_window,
                      text='Вибір категорії додатку (1/2)').grid(row=11, sticky=W)

                def change_cat_selector(event=None):
                    if big_cat.get() == 'Hyper Casual':
                        values = ['.io', 'Ball', 'Dexterity', 'Idle', 'Merge', 'Puzzle', 'Rising/Falling', 'Stacking',
                                  'Swerve', 'Tap / Timing', 'Turning', 'Other']
                    elif big_cat.get() == 'AR/Location Based':
                        values = ['AR/Location Based']
                    elif big_cat.get() == 'Puzzle':
                        values = ['Action Puzzle', 'Board', 'Bubble Shooter', 'Coloring Games', 'Crossword',
                                  'Hidden Objects', 'Jigsaw', 'Match 3', 'Non Casino Card Game', 'Solitaire', 'Trivia',
                                  'Word', 'Other Puzzle']
                    elif big_cat.get() == 'Arcade':
                        values = ['Endless Runner', 'Idler', 'Platformer', 'Shoot ’em Up', 'Tower Defense',
                                  'Other Arcade']
                    elif big_cat.get() == 'Lifestyle':
                        values = ['Customization', 'Interactive Story', 'Music/Band', 'Other Lifestyle']
                    elif big_cat.get() == 'Simulation':
                        values = ['Adventures', 'Breeding', 'Cooking/Time Management', 'Farming', 'Idle Simulation',
                                  'Sandbox', 'Tycoon/Crafting', 'Other Simulation']
                    elif big_cat.get() == 'Other Casual':
                        values = ['Other Casual']
                    elif big_cat.get() == 'Lucky Rewards':
                        values = ['Lucky Casino', 'Lucky Game Discovery', 'Lucky Puzzle']
                    elif big_cat.get() == 'Kids & Family':
                        values = ['Kids & Family']
                    elif big_cat.get() == 'Casino':
                        values = ['Bingo', 'Blackjack', 'Non-Poker Cards', 'Poker', 'Slots', 'Sports Betting',
                                  'Other Casino']
                    elif big_cat.get() == 'Shooter':
                        values = ['Battle Royale', 'Classic FPS', 'Snipers', 'Tactical Shooter', 'Other Shooter']
                    elif big_cat.get() == 'RPG':
                        values = ['Action RPG', 'Fighting', 'Idle RPG', 'MMORPG', 'Puzzle RPG', 'Survival',
                                  'Turn-based RPG', 'Other RPG']
                    elif big_cat.get() == 'Card Games':
                        values = ['Card Battler']
                    elif big_cat.get() == 'Strategy':
                        values = ['4X Strategy', 'Build & Battle', 'Idle Strategy', 'MOBA', 'Sync. Battler',
                                  'Other Strategy']
                    elif big_cat.get() == 'Other Mid-Core':
                        values = ['Other Mid-Core']
                    elif big_cat.get() == 'Sports & Racing':
                        values = ['Other Sports & Racing', 'Casual Racing', 'Other Racing', 'Simulation Racing',
                                  'Casual Sports', 'Licensed Sports']
                    elif big_cat.get() == 'Non-Gaming':
                        values = ['Books & Reference', 'Comics', 'Communications', 'Dating', 'Education',
                                  'Entertainment', 'Events & Tickets', 'Finance', 'Food & Drink', 'Health & Fitness',
                                  'Lifestyle', 'Maps & Navigation', 'Medical', 'Music & Audio', 'News & Magazines',
                                  'Parenting', 'Personalization', 'Photography', 'Real Estate & Home', 'Marketplace',
                                  'Shopping', 'Social', 'Sports', 'Bike', 'Car Sharing', 'Taxi/Ride Sharing',
                                  'Travel & Local', 'Travel Air & Hotel', 'Other Non-Gaming']
                    else:
                        raise Exception('wrong category IronSource')

                    categories = Combobox(master=new_window,
                                          state='readonly',
                                          values=values,
                                          textvariable=cat_var)

                    categories.current(0)
                    Label(master=new_window,
                          text='Вибір категорії додатку (2/2)').grid(row=13, sticky=W)
                    categories.grid(row=14, sticky=W)

                cat_var = StringVar()
                big_cat_var = StringVar()
                big_cat = Combobox(master=new_window,
                                   state='readonly',
                                   values=['Hyper Casual', 'AR/Location Based', 'Puzzle', 'Arcade',
                                           'Lifestyle', 'Simulation', 'Kids & Family', 'Lucky Rewards', 'Other Casual',
                                           'Casino', 'Shooter', 'RPG', 'Card Games', 'Strategy', 'Other Mid-Core',
                                           'Sports & Racing', 'Non-Gaming'],
                                   textvariable=big_cat_var)
                big_cat.grid(row=12, sticky=W)
                big_cat.current(0)
                change_cat_selector()
                big_cat.bind("<<ComboboxSelected>>", change_cat_selector)
                Button(master=new_window,
                       text='Запуск',
                       command=lambda: messagebox.showinfo(
                           message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                      mediator=mediator,
                                                      ad_service=ad_service,
                                                      app_category=cat_var.get(),
                                                      trash=big_cat_var.get())
                       )).grid(row=18, sticky=W)

            case AdServices.MyTargetKids.value | AdServices.MyTargetAdults.value:

                check_button_var = IntVar()
                Checkbutton(master=new_window, text='social, dating, smoking, casino, bookie',
                            variable=check_button_var).grid(row=9, sticky=W)
                Button(master=new_window,
                       text='Запуск',
                       command=lambda: messagebox.showinfo(
                           message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                      mediator=mediator,
                                                      ad_service=ad_service,
                                                      categories=["social", "dating", "smoking", "casino",
                                                                  "bookie"] if check_button_var.get() else [])
                       )).grid(row=10, sticky=W)

            case AdServices.ChartBoost.value:

                coppa_var = IntVar()

                Checkbutton(master=new_window,
                            text='Coppa',
                            variable=coppa_var).grid(row=4, sticky=W)

                orientation_var = StringVar()
                Radiobutton(master=new_window,
                            text=ChartBoostOrientations.portrait.name,
                            value=ChartBoostOrientations.portrait.name,
                            variable=orientation_var,
                            command=activate_btn).grid(row=6, sticky=W)
                Radiobutton(master=new_window,
                            text=ChartBoostOrientations.landscape.name,
                            value=ChartBoostOrientations.landscape.name,
                            variable=orientation_var,
                            command=activate_btn).grid(row=7, sticky=W)
                Radiobutton(master=new_window,
                            text=ChartBoostOrientations.both.name,
                            value=ChartBoostOrientations.both.name,
                            variable=orientation_var,
                            command=activate_btn).grid(row=8, sticky=W)

                btn = Button(master=new_window,
                             text='Запуск',
                             state=DISABLED,
                             command=lambda: messagebox.showinfo(
                                 message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                            mediator=mediator,
                                                            ad_service=ad_service,
                                                            orientation=InputToChartBoostConvertor.orientation(
                                                                orientation_var.get()),
                                                            coppa=coppa_var.get()
                                                            )
                             ))

                btn.grid(row=10, sticky=W)

            # case AdServices.TapJoy.value:
            #
            #     orientation_var = StringVar()
            #     Label(master=new_window,
            #           text='Orientation').grid(row=3, sticky=W)
            #     orientation_selector = Combobox(master=new_window,
            #                                     state='readonly',
            #                                     values=['both', 'portrait', 'landscape'],
            #                                     textvariable=orientation_var)
            #     orientation_selector.current(0)
            #     orientation_selector.grid(row=4, sticky=W)
            #     maturity_var = StringVar()
            #     cat1_var = IntVar()
            #     cat2_var = IntVar()
            #     cat3_var = IntVar()
            #     cat4_var = IntVar()
            #     maturity_selector = Combobox(master=new_window,
            #                                  state='readonly',
            #                                  values=['Everyone', 'Low', 'Medium', 'High', 'Mature'],
            #                                  textvariable=maturity_var)
            #     maturity_selector.current(0)
            #
            #     Label(master=new_window,
            #           text='Maturity settings on the ads').grid(row=5, sticky=W)
            #     maturity_selector.grid(row=6, sticky=W)
            #     Checkbutton(master=new_window,
            #                 text='Gambling',
            #                 variable=cat1_var).grid(row=7, sticky=W)
            #     Checkbutton(master=new_window,
            #                 text='Alcohol',
            #                 variable=cat2_var).grid(row=8, sticky=W)
            #     Checkbutton(master=new_window,
            #                 text='Dating',
            #                 variable=cat3_var).grid(row=9, sticky=W)
            #     Checkbutton(master=new_window,
            #                 text='Politics',
            #                 variable=cat4_var).grid(row=10, sticky=W)
            #     Button(master=new_window,
            #            text='Запуск',
            #            command=lambda: messagebox.showinfo(
            #                message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
            #                                           mediator=mediator,
            #                                           ad_service=ad_service,
            #                                           mature=FrontToTapjoyConvertor.maturity(maturity_var.get()),
            #                                           orientation=orientation_var.get(),
            #                                           categories=FrontToTapjoyConvertor.categories([cat1_var.get(),
            #                                                                                         cat2_var.get(),
            #                                                                                         cat3_var.get(),
            #                                                                                         cat4_var.get()])
            #                                           ))).grid(
            #         row=11,
            #         sticky=W)

            case AdServices.AdColony.value:

                # Label(new_window, text='Виберіть категорії реклами які відключаємо').grid(row=5, column=0, sticky=W)
                # ad_cat_of = StringVar()
                # Radiobutton(master=new_window,
                #             text='PG: Politics, Religion, Gambling, Apps(13-16), Apps(17+), VideoGames(Teen), '
                #                  'VideoGames(Mature, Adults Only), TV(PG-14), TV(MA), Personal Ads, Alcohol, '
                #                  'Sexual & Reproductive Health, References to Sex & Sexuality, Get Rich Quick, '
                #                  'Drugs & Supplements, Cosmetic, Black Magic, Weight Loss, Lottery',
                #             value='PG',
                #             variable=ad_cat_of,
                #             command=activate_btn).grid(row=6, sticky=W)
                # Radiobutton(master=new_window,
                #             text='Kids: Politics, Religion, Gambling, Movies & Entertainment(PG, PG-13), Apps(8-12), '
                #                  'Apps(13-16), Apps(17+), VideoGames(E 10+), VideoGames(Teen), '
                #                  'VideoGames(Mature, Adults Only), TV(PG-14), TV(MA), Personal Ads, Alcohol, '
                #                  'Sexual & Reproductive Health, References to Sex & Sexuality, Get Rich Quick, '
                #                  'Drugs & Supplements, Cosmetic, Black Magic, Weight Loss, Lottery',
                #             value='Kids',
                #             variable=ad_cat_of,
                #             command=activate_btn).grid(row=7, sticky=W)
                # Radiobutton(master=new_window,
                #             text='Teens: Politics, Religion, Gambling, Apps(17+), VideoGames(Mature, Adults Only), '
                #                  'TV(MA), Personal Ads, Alcohol, Sexual & Reproductive Health, '
                #                  'References to Sex & Sexuality, Get Rich Quick, Drugs & Supplements, Cosmetic, '
                #                  'Black Magic, Weight Loss, Lottery',
                #             value='Teens',
                #             variable=ad_cat_of,
                #             command=activate_btn).grid(row=8, sticky=W)
                # Radiobutton(master=new_window,
                #             text='Mature: Politics, Religion, Gambling, VideoGames(Mature, Adults Only), TV(MA), '
                #                  'Personal Ads, Alcohol, Sexual & Reproductive Health, References to Sex & Sexuality, '
                #                  'Get Rich Quick, Drugs & Supplements, Lottery',
                #             value='Mature',
                #             variable=ad_cat_of,
                #             command=activate_btn).grid(row=9, sticky=W)
                # Radiobutton(master=new_window,
                #             text='Adults',
                #             value='Adults',
                #             variable=ad_cat_of,
                #             command=activate_btn).grid(row=10, sticky=W)

                btn = Button(master=new_window,
                             text='Запуск',
                             command=lambda: messagebox.showinfo(message='Success'))
                btn.grid(row=11, sticky=W)

            case AdServices.InmobiKids.value | AdServices.InmobiAdults.value:

                kids = True
                categories_selector_variable = StringVar()
                state = ACTIVE
                if ad_service == 'InmobiAdults':
                    state = DISABLED
                    consent_of_age = StringVar()
                    kids = False
                    Label(new_window,
                          text='Виберіть налаштування реклами').grid(row=3, column=0, sticky=W)
                    categories_selector = Combobox(master=new_window,
                                                   state='readonly',
                                                   values=['Adults', 'Mature', 'Meedlight Filter', 'Teens',
                                                           'Dating, Gambling, Prnography', 'Gambling+'],
                                                   textvariable=categories_selector_variable)
                    categories_selector.current(0)
                    categories_selector.grid(row=4)
                    Label(new_window,
                          text='Виберіть цільову авдиторію').grid(row=5, column=0, sticky=W)
                    Radiobutton(master=new_window,
                                text='mixed (teens)',
                                value=str(InmobiConsentOfAgeId.teens.value),
                                variable=consent_of_age,
                                command=activate_btn).grid(row=6, sticky=W)
                    Radiobutton(master=new_window,
                                text='adults',
                                value=str(InmobiConsentOfAgeId.adults.value),
                                variable=consent_of_age,
                                command=activate_btn).grid(row=7, sticky=W)
                btn = Button(master=new_window,
                             text='Запуск',
                             command=lambda: messagebox.showinfo(
                                 message=unit_auto_creating(
                                     bundle=bundle_entry.get().replace('\n', ''),
                                     mediator=mediator,
                                     ad_service=ad_service,
                                     mature=InmobiConsentOfAgeId.kids.value if kids else int(consent_of_age.get()),
                                     categories=FrontToInmobiConvertor.get_categories_id(
                                         name=categories_selector_variable.get(),
                                         kids=kids))),
                             state=state)
                btn.grid(row=8, sticky=W)

            case AdServices.Yandex.value | AdServices.VungleKids.value | AdServices.VungleAdults.value | AdServices.MaxKids.value | AdServices.MaxAdults.value:

                Button(master=new_window,
                       text='Запуск',
                       command=lambda: messagebox.showinfo(
                           message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                      mediator=mediator,
                                                      ad_service=ad_service))).grid(
                    row=11, sticky=W)

            case AdServices.DTExchange.value:

                coppa_var = BooleanVar()
                Checkbutton(master=new_window,
                            text='COPPA',
                            variable=coppa_var,
                            onvalue=1,
                            offvalue=0).grid(row=10, sticky=W)
                Button(master=new_window,
                       text='Запуск',
                       command=lambda: messagebox.showinfo(
                           message=unit_auto_creating(bundle=bundle_entry.get().replace('\n', ''),
                                                      mediator=mediator,
                                                      ad_service=ad_service,
                                                      coppa=coppa_var.get()))).grid(
                    row=11, sticky=W)

            case _:
                print("Wrong Selection")

    def get_tokens_menu(self):
        new_window = Toplevel(master=self.root)
        new_window.title("Оновлення токенів")
        row = 0
        ad_services_with_tokens = [
            AdServices.UnityKids.value,
            AdServices.UnityAdults.value,
            AdServices.Yandex.value,
            AdServices.MyTarget.value,
            # AdServices.TapJoy.value,
            AdServices.InmobiKids.value,
            AdServices.InmobiAdults.value,
            AdServices.AdColony.value,
            AdServices.DTExchange.value
        ]
        for ad_service in ad_services_with_tokens:
            label = Label(master=new_window, text=ad_service)
            label.grid(row=row, sticky=W)
            token = AdServiceToTokenConvertor.convert(ad_service)
            Button(master=new_window,
                   text=ad_service,
                   command=lambda _token=token, _label=label: messagebox.showinfo(
                       message=_token(kids=True if 'kids' in _label.cget('text').lower() else False).send_new_token()
                   )).grid(row=row, column=1, sticky=W)
            row += 1
        Label(master=new_window,
              text='Всі').grid(row=row, sticky=W)
        Button(master=new_window,
               text='Оновити',
               command=lambda: messagebox.showinfo(message=renew_all())).grid(row=row, column=1, sticky=W)
