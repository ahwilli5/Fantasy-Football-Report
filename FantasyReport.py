import os
import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.styles import ParagraphStyle


#Input your own league ID and the year that you are interested in
#League ID is 5 digit code that is specific to your fantasy league
league_id = #####
tm_name = int(input('What team are you interested in? (1-12) \n 1:Grant, 2:Reeve, 3:Sturdy, 4:Ne ,5:Jamal, 6:Austin, 7:Danny, 8:Rob, 9:TRay, 10:Crowe, 11:Fawal, 12:Peyton'))
#tm_name = 4
#year = 2019
year = int(input('What year are you interested in? (2013-2019 only)'))

#team dict should be updated for your specific league

dict = {1:'Grant', 2:'Reeve', 3:'Sturdy', 4:'Ne' ,5:'Jamal', 6:'Austin', 7:'Danny', 8:'Rob', 9:'TRay', 10:'Crowe', 11:'Fawal', 12:'Peyton'}
xlabels = dict.values()
# enter swid and espn s2

#Generate the league data from that year
# for year=2019, this doesn't need the [0]

if int(year) < 2019:
    url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
          str(league_id) + "?seasonId=" + str(year)
    r = requests.get(url, cookies={"swid": "{#######-######-####-######-######}", #swid and espn_s2 are specific to the account
                                   "espn_s2": "########"}
                     , params={"view": "mMatchup"})
    d = r.json()[0]
    df_temp = []
    for game in range(len(d['schedule'])):
        if d['schedule'][game].get('away') is not None:
            df_temp.append([d['schedule'][game].get('matchupPeriodId'),
                            d['schedule'][game].get('home').get('teamId'),
                            d['schedule'][game].get('home').get('totalPoints'),
                            d['schedule'][game].get('home').get('totalPoints') - d['schedule'][game].get('away').get(
                                'totalPoints'),
                            d['schedule'][game].get('away').get('teamId'),
                            d['schedule'][game].get('away').get('totalPoints'),
                            d['schedule'][game].get('away').get('totalPoints') - d['schedule'][game].get('home').get(
                                'totalPoints')])
            df = pd.DataFrame(df_temp, columns=['Week', 'Team1', 'Score1', 'Margin1', 'Team2', 'Score2', 'Margin2'])
else:
    url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
          str(year) + "/segments/0/leagues/" + str(league_id)
    r = requests.get(url, cookies={"swid": "{F3173C47-ECAE-4E0F-973C-47ECAE2E0F8F}",
                                   "espn_s2": "AEBLjLzYKQejWSpl8mCFdjSvKAB3jJdGJWwBpVhQpFzZ4RJAmUkoyuP6uC%2BQdSY3UCys97eLDdhBmS7r4LqBtDhIBk%2BwL50w7MltRyiBDp2CGobL1%2FzxlMXwTLqDZVr3srlg9lSxlsAB72acFfGxAU5vCg6TdANLe0QEQ5s8K0MTUBP3fYH6HyuHt5MLk789wBeoZmNvVtY0Ehu5r7%2Bk7mbl4L6LzN7js4KOL9Lim6buzaa%2FaWrYJBoJRdjffqLjiLrsUktto9Qgnr5Wat01i34v"}
                     , params={"view": "mMatchup"})
    d = r.json()
    df_temp = []
    for game in range(len(d['schedule'])):
        if d['schedule'][game].get('away') is not None:
            df_temp.append([d['schedule'][game].get('matchupPeriodId'),
                            d['schedule'][game].get('home').get('teamId'),
                            d['schedule'][game].get('home').get('totalPoints'),
                            d['schedule'][game].get('home').get('totalPoints') - d['schedule'][game].get('away').get(
                                'totalPoints'),
                            d['schedule'][game].get('away').get('teamId'),
                            d['schedule'][game].get('away').get('totalPoints'),
                            d['schedule'][game].get('away').get('totalPoints') - d['schedule'][game].get('home').get(
                                'totalPoints')])
            df = pd.DataFrame(df_temp, columns=['Week', 'Team1', 'Score1', 'Margin1', 'Team2', 'Score2', 'Margin2'])
df2 = []

for game in range(len(d['schedule'])):
    if d['schedule'][game].get('away') is not None:
        df2.append([d['schedule'][game].get('matchupPeriodId'),
            d['schedule'][game].get('home').get('teamId'),
            d['schedule'][game].get('home').get('totalPoints'),
            d['schedule'][game].get('home').get('totalPoints') - d['schedule'][game].get('away').get(
                'totalPoints'),
            d['schedule'][game].get('away').get('teamId'),
            d['schedule'][game].get('away').get('totalPoints'),
            d['schedule'][game].get('away').get('totalPoints') - d['schedule'][game].get('home').get(
                'totalPoints')])

df2 = pd.DataFrame(df2, columns=['Week', 'Team1', 'Score1', 'Margin1', 'Team2', 'Score2', 'Margin2'])
avgs = (df2.filter(['Week', 'Score1', 'Score2']).melt(id_vars=['Week'], value_name='Score').groupby('Week').mean().reset_index())

image_dir = os.getcwd() + "/Images/"
#logo = image_dir + "LOGO.png"

wins_df = [0,0,0,0,0,0,0,0,0,0,0,0]
loss_df = [0,0,0,0,0,0,0,0,0,0,0,0]
points_df = [0,0,0,0,0,0,0,0,0,0,0,0]

for team in dict.keys():
    tempdf = df2.query('Team1 == @team | Team2 == @team').reset_index(drop=True)
    templist = list(tempdf['Team2'] == team)
    tempdf.loc[templist, ['Team1', 'Score1', 'Team2', 'Score2']] = \
        tempdf.loc[templist, ['Team2', 'Score2', 'Team1', 'Score1']].values
    # add new score and win cols
    tempdf = (tempdf
           .assign(Chg1=tempdf['Score1'] - avgs['Score'],
                   Chg2=tempdf['Score2'] - avgs['Score'],
                   Win=tempdf['Score1'] > tempdf['Score2']))

    wins = len(tempdf[tempdf['Win'] == True])
    losses = len(tempdf[tempdf['Win'] == False])
    wins_df[team-1] = wins
    loss_df[team-1] = losses
    for week in range(len(tempdf['Week'])):
        score = tempdf['Score1'][week]
        points_df[team-1] += score

record_df = pd.DataFrame({'Wins': wins_df, 'Losses': loss_df}, index=dict.keys())

# grab all games with this team
df3 = df2.query('Team1 == @tm_name | Team2 == @tm_name').reset_index(drop=True)
# move the team of interest to "Team1" column
ix = list(df3['Team2'] == tm_name)
df3.loc[ix, ['Team1', 'Score1', 'Team2', 'Score2']] = \
    df3.loc[ix, ['Team2', 'Score2', 'Team1', 'Score1']].values

# add new score and win cols
df3 = (df3
       .assign(Chg1=df3['Score1'] - avgs['Score'],
               Chg2=df3['Score2'] - avgs['Score'],
               Win=df3['Score1'] > df3['Score2']))

df3_wins = df3[df3['Win'] == True]
df3_losses = df3[df3['Win'] == False]

x_wins = np.array(df3_wins['Chg1'])
x_losses = np.array(df3_losses['Chg1'])

y_wins = np.array(df3_wins['Chg2'])
y_losses = np.array(df3_losses['Chg2'])

lucky_wins = 0
deserved_losses = 0
deserved_wins = 0
unlucky_losses = 0

for z in range(len(df3.Win)):
    if df3.Win[z] == True and df3['Score1'][z] < avgs['Score'][z]:
        lucky_wins = lucky_wins + 1
    if df3.Win[z] == False and df3['Score1'][z] < avgs['Score'][z]:
        deserved_losses = deserved_losses + 1

    if df3.Win[z] == False and df3['Score1'][z] > avgs['Score'][z]:
        unlucky_losses = unlucky_losses + 1
    if df3.Win[z] == True and df3['Score1'][z] > avgs['Score'][z]:
        deserved_wins = deserved_wins + 1

total_wins = lucky_wins + deserved_wins
winluck = (lucky_wins / total_wins) * 100

total_losses = deserved_losses + unlucky_losses
lossluck = (unlucky_losses / total_losses) *100
total_luck = (lucky_wins - unlucky_losses) *10


class Visualization:
    def league_record(self):
        plt.figure(figsize=(16, 6))  # 10 is width, 4 is height

        # Left hand side plot
        plt.subplot(1, 2, 1)  # (nRows, nColumns, axes number to plot)
        sns.barplot(x=record_df.index, y=points_df, palette='muted')
        plt.title('Total Points Scored on Season')
        plt.xlabel('team')
        plt.ylabel('Points Scored')
        plt.xticks(range(len(xlabels)), xlabels, fontsize=10)

        # Right hand side plot
        plt.subplot(1, 2, 2)
        sns.barplot(x=record_df.index, y=record_df['Wins'], palette='muted')
        plt.title('Number of Wins on Season')
        plt.xlabel('team')
        plt.ylabel('Wins on Season')
        plt.xticks(range(len(xlabels)), xlabels, fontsize=10)
        plt.savefig(image_dir + 'league_record.png', dpi=400)
        plt.clf()

    def box_whisker(self):
        print('Making Box and Whisker Plot...')
        df_BaW = pd.DataFrame(df[['Week', 'Team1', 'Margin1']]).rename(columns={'Team1': 'Team', 'Margin1': 'Margin of Loss or Victory'})
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        sns.boxplot(x='Team', y='Margin of Loss or Victory', data=df_BaW, palette='muted')
        sns.swarmplot(x='Team', y='Margin of Loss or Victory', data=df_BaW, palette='muted', edgecolor='black')
        xlabels = dict.values()
        ax.axhline(0, ls='--', color = 'k')
        ax.set_title('Win/Loss Margins ' + str(year), fontsize=16)
        plt.xticks(range(len(xlabels)), xlabels, fontsize=16)
        plt.savefig(image_dir + 'box_whisker.png', dpi=400)
        plt.clf()


    def lucky_plot(self):

        print('Making Luckyness Plot...')
        fig, ax = plt.subplots(1, 1, figsize=(16, 6))
        plt.title("How Good Was " + dict[tm_name] + " Really in " + str(
            year) + "? " + "Each point is a game from that regular season. \n Total Record:" +
                  str(total_wins) + '-' + str(total_losses), fontsize=16)
        plt.plot(x_wins, y_wins, 'go', label='wins')
        plt.plot(x_losses, y_losses, 'rx', label='losses')
        x1 = np.arange(-60, 60)
        x2 = np.zeros(120)
        y3 = np.zeros(120)
        y1 = np.arange(-60, 60)
        plt.xlabel('POINTS FOR Compared to League Avg.', fontsize=16)
        plt.ylabel("POINTS AGAINST Comp'd to Lg. Avg.", fontsize=16)
        plt.plot(x1, y1, color='black', linestyle=':')
        # im = ax.imshow(z, aspect='auto', extent=[xmin, xmax, ymin, ymax],     origin='lower', zorder=zorder)
        plt.plot(x1, y1 * (-1), color='black', linestyle=':')
        plt.plot(x1, y3, color='black')
        plt.fill_between(x1, 60, y1, facecolor='red', interpolate=True, alpha=0.2)
        plt.fill_between(x1, -60, y1, facecolor='green', interpolate=True, alpha=0.2)
        plt.plot(x2, y1, color='black')
        plt.annotate('Good Win', (39, 25), color='g', fontsize=16)
        plt.annotate('Lucky Win', (-45, -50), color='g', fontsize=16)
        plt.annotate('Unlucky Loss', (15, 50), color='r', fontsize=16)
        plt.annotate('Deserved Loss', (-55, -25), color='r', fontsize=16)
        plt.annotate('On the season, ' + dict[tm_name] + ' had ' + str(lucky_wins) + ' lucky wins, ' + str(deserved_losses) + ' deserved losses, \n\n' +
                     str(deserved_wins) + ' deserved wins, and ' + str(unlucky_losses) + ' unlucky losses.\n He was ~' + str(round(total_luck,0)) + '% lucky over the season.', (-55, 30),
                     color='black', fontsize=16)
        plt.legend(loc='best', fontsize=14)
        plt.savefig(image_dir + 'lucky_plot.png', dpi=400)
        plt.clf()


    def gen_pdf(self):
        print('Combining Images into PDF.....')
        path1 = image_dir + 'box_whisker.png'
        path2 = image_dir + 'lucky_plot.png'
        path3 = image_dir + 'league_record.png'

        pdf = PdfFileWriter()

        # Using ReportLab Canvas to insert image into PDF
        imgTemp = BytesIO()
        imgDoc = canvas.Canvas(imgTemp, pagesize=(2000, 2300))


        # box and whisker x, y - start position
        imgDoc.drawImage(path1, 50, 700, width=1800,height=750)
        # lucky plot
        imgDoc.drawImage(path2, 50, 0, width=1800, height=700)
        # record and points
        imgDoc.drawImage(path3, 50, 1400, width=1800, height=700)


        # draw three lines, x,y,width,height
        imgDoc.rect(0.83 * inch, 28.5 * inch, 26.0 * inch, 0.04 * inch, fill=1)
        imgDoc.rect(0.83 * inch, 19.5* inch, 26.0 * inch, 0.04 * inch, fill=1)
        imgDoc.rect(0.83 * inch, 9.75 * inch, 26.0 * inch, 0.04 * inch, fill=1)

        # title
        imgDoc.setFont('Helvetica-Bold', 82)
        imgDoc.drawString(212, 2078, "Fantasy Football Year-End Report for "+ str(year), )

        imgDoc.save()
        pdf.addPage(PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0))
        pdf.write(open("Fantasy_Report.pdf","wb"))
        print('Congratulations! You have successfully created your year-end Fantasy Football report!')
        if sys.platform == "win32":
            os.startfile("Fantasy_Report.pdf")
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, "Fantasy_Report.pdf"])




if __name__ == "__main__":
    visual = Visualization()
    visual.league_record()
    visual.box_whisker()
    visual.lucky_plot()
    visual.gen_pdf()
