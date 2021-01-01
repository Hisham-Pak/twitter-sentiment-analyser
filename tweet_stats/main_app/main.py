from .extract_text import *
from .replies import *

Reportdf = pd.DataFrame(columns=['Categories', '% Alarming', '% Positive', '% Negative'])

Admin_Replies = {
    'JEAN MARC KABUND':             'Reply',
    '2 BONBONS':                    'Reply',
    'KABUYA':                       'Reply',
    'WEWA':                         'Reply',
    'TALIBAN':                      'Reply',
    'TSHISEKEDISTE':                'Reply',
    'LUBA':                         'Reply',
    'KASAI':                        'Reply',
    'BALUBA':                       'Reply',
    'FATSHI':                       'Reply',
    'FELIX':                        'Reply',
    'TSHISEKEDI':                   'Reply',
    'TSHILOMBO':                    'Reply',
    'BETON':                        'Reply',
    'KITENGE YESU':                 'Reply',
    'TINA SALAMA':                  'Reply',
    'FAYULU':                       'Reply',
    'MARTIN FAYULU':                'Reply',
    'MADIDI':                       'Reply',
    'MOISE KATUMBI':                'Reply',
    'JEAN PIERRE BEMBA':            'Reply',
    'MUZITO':                       'Reply',
    'MOZITO':                       'Reply',
    'MUZITU':                       'Reply',
    'JOSEPH KABILA':                'Reply',
    'KABANGE':                      'Reply',
    'KANAMBE':                      'Reply',
    'SHINA RAMBO':                  'Reply',
    'YEMEYI':                       'Reply',
    'YE MEYI':                      'Reply',
    'KABILISTE':                    'Reply',
    'MINAKU':                       'Reply',
    'AUBIN MINAKU':                 'Reply',
    'THAMBUE MUAMBA':               'Reply',
    'ATM':                          'Reply',
    'TAMBUE MWAMBA':                'Reply',
    'MABUNDA':                      'Reply'
}

Categories = {
    "PRESIDENCE_RDC" :    ['FATSHI', 'TSHISEKEDI', 'TSHILOMBO', 'BETON', 'KITENGE YESU', 'TINA SALAMA'],
    "UDPS" :              ['JEAN MARC KABUND', '2 BONBONS', 'KABUYA', 'WEWA', 'TALIBAN', 'TSHISEKEDISTE', 'LUBA', 'KASAI', 'BALUBA'],
    "Opposition":         ['FAYULU', 'MARTIN FAYULU', 'MADIDI', 'MOISE KATUMBI', 'JEAN PIERRE BEMBA', 'MUZITO', 'MOZITO', 'MUZITU'],
    "FCC" :               ['JOSEPH KABILA', 'KABANGE', 'KANAMBE', 'SHINA RAMBO', 'YEMEYI', 'YE MEYI', 'KABILISTE', 'MINAKU', 'AUBIN MINAKU', 'THAMBUE MUAMBA', 'ATM', 'TAMBUE MWAMBA', 'MABUNDA']
}

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def RetrieveTweetstoCSV():
    category_details_list = []
    for Category in Categories.keys():
        print(Category)
        with pd.ExcelWriter(os.path.join(BASE_DIR, f'output_{Category}.xlsx')) as writer:
            # Creating Subcategory List
            SubCategoryList = Categories[Category]

            TotalAlarming = 0
            TotalPositive = 0
            TotalNegative = 0

            Total_SubCategory_Tweets = 0        # Total Overall Tweets

            TempResultList = []
            for SubCategory in SubCategoryList:
                # Retrieving Tweets
                print("Extracting Tweets for Word: " + SubCategory + ' .......')
                TweetDataFrame = TwitterHashtag('#' + SubCategory)

                # If Tweets are retrieved
                if TweetDataFrame is not None:
                    print("Retrieved " + str(len(TweetDataFrame.index)) + ' Tweets for Word: ' + SubCategory)
                    print()
                    Total_SubCategory_Tweets += len(TweetDataFrame.index)      # Total Number of Tweets

                    SentimentAnalysis(TweetDataFrame)

                    LabelList = TweetDataFrame['Sentiment'].value_counts().index.tolist()
                    ValueList = TweetDataFrame['Sentiment'].value_counts(normalize=True).tolist()

                    # Categorizing on Sentiment Base
                    for index, Label in enumerate(LabelList):
                        if Label == 'Alarming':
                            Alarming_Percentage = round(ValueList[index] * 100, 3)
                            TotalAlarming += int(ValueList[index] * len(TweetDataFrame.index))

                        elif Label == 'Positive':
                            Positive_Percentage = round(ValueList[index] * 100, 3)
                            TotalPositive += int(ValueList[index] * len(TweetDataFrame.index))

                        elif Label == 'Negative':
                            Negative_Percentage = round(ValueList[index] * 100, 3)
                            TotalNegative += int(ValueList[index] * len(TweetDataFrame.index))


                    try:
                        Alarming_Percentage
                    except NameError:
                        Alarming_Percentage = 0.00

                    try:
                        Positive_Percentage
                    except NameError:
                        Positive_Percentage = 0.00

                    try:
                        Negative_Percentage
                    except NameError:
                        Negative_Percentage = 0.00

                    TempResultList.append([SubCategory, Alarming_Percentage, Positive_Percentage, Negative_Percentage])

                    # Reply to Tweets
                    #ReplyTweet(TweetDataFrame, Admin_Replies[SubCategory])    # With Admin Replies
                    #ReplyTweet(TweetDataFrame, 'None')                     # With Positive Tweets

                    # Sort By Date
                    TweetDataFrame = TweetDataFrame.sort_values('Date Created', ascending=False)

                    # Adding a Sheet To Excel File
                    TweetDataFrame.to_excel(writer, sheet_name=SubCategory)

                # If No Tweets are Retrieved
                else:
                    TempResultList.append([SubCategory, 0.00, 0.00, 0.00])

                # sub_category details
                category_details_list.append([Category, SubCategory, TotalPositive, TotalNegative, TotalAlarming,\
                    Positive_Percentage, Negative_Percentage, Alarming_Percentage])

            if Total_SubCategory_Tweets != 0:
                # Adding Category
                Reportdf.loc[len(Reportdf)] = [Category, round((TotalAlarming * 100)/Total_SubCategory_Tweets, 3), round((TotalPositive * 100)/Total_SubCategory_Tweets, 3), round((TotalNegative * 100)/Total_SubCategory_Tweets, 3)]

                # Adding Sub Categories
                for Result in TempResultList:
                    Reportdf.loc[len(Reportdf)] = Result

            else:   # If Unfortunately No Tweets are Retrieved
                # Adding Category
                Reportdf.loc[len(Reportdf)] = [Category, 0.00, 0.00, 0.00]

                # Adding Sub Categories
                for cat in SubCategoryList:
                    Reportdf.loc[len(Reportdf)] = [cat, 0.00, 0.00, 0.00]

            # Leaving a Row After Every Category
            Reportdf.loc[Reportdf.iloc[-1].name + 1, :] = np.nan

            writer.close()

        # Creating a Result CSV
    Reportdf.to_csv('Output.csv', index=False, header=True)
    
    return Reportdf, category_details_list

if __name__ == "__main__":
    Reportdf = RetrieveTweetstoCSV()
    print(Reportdf)