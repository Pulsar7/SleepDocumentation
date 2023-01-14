"""
@Name: Sleepdoku - Visualization
@Author: Benedikt Fichtner
@2022 (gregorianischer Kalender)/Version 2.0/Visualizer
"""
import sys,numpy as np
import matplotlib.pyplot as plt
from rich.table import Table
from rich.tree import Tree
from rich import print as pr

class VISUALIZE():
    def __init__(self,console,db,tables,note_seperator:str) -> None:
        (self.console,self.db, self.tables) = (console,db,tables)
        self.month_names = ["Jan","Feb","Mar","Apr","Mai","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        self.note_seperator:str = note_seperator

    def create_figures(self) -> None:
        (fig, ax) = plt.subplots(2, 2, constrained_layout=True)
        (fig2,ax2) = plt.subplots(1, 2, constrained_layout=True)
        (fig3,ax3) = plt.subplots(1, 1, constrained_layout=True)
        fig.suptitle("Wet bed, Average sleep duration & Wake-up-mood")
        fig2.suptitle("Bedtime & Wake-Up-Time (hours:minutes)")
        fig3.suptitle("Sleep duration of each day (in hours)")
        fig.set_figwidth(13)
        fig.set_figheight(7)
        fig2.set_figwidth(13)
        fig2.set_figheight(7)
        fig3.set_figwidth(13)
        fig3.set_figheight(7)
        (self.fig,self.fig2,self.fig3,self.ax,self.ax2,self.ax3) = (fig,fig2,fig3,ax,ax2,ax3)

    def get_months_and_years(self,days:dict) -> tuple((list[str],list[str])):
        months:list[str] = []
        years:list[str] = []
        for date in days:
            month:str = int(date.split("-")[1])
            year:str = int(date.split("-")[2])
            if month not in months:
                months.append(month)
            if year not in years:
                years.append(year)
        return (months,years)

    def build_bedtime_and_wake_up_time_pies(self,data:dict) -> None:
        ### Bedtime overview - percent (hours:minutes)
        year_data:dict = data
        bedtimes:list = []
        wake_up_times:list = []
        for day in year_data:
            bedtime:str = year_data[day]['bedtime']
            (hours, minutes) = self.adjust_hours_and_minutes(time = bedtime)
            bedtimes.append(f"{hours}:{minutes}")
            wake_up_time:str = year_data[day]['wake_up_time']
            (hours, minutes) = self.adjust_hours_and_minutes(time = wake_up_time)
            wake_up_times.append(f"{hours}:{minutes}")
        #### Bedtime
        labels = []
        explode = []
        sizes = []
        this_sizes = {}
        for bedtime in bedtimes:
            if bedtime not in this_sizes:
                this_sizes[bedtime] = 0
                labels.append(bedtime)
                explode.append(0)
            this_sizes[bedtime] += 1
        for bedtime in this_sizes:
            percent:float = (100/len(bedtimes))*this_sizes[bedtime]
            sizes.append(percent)
        explode[sizes.index(max(sizes))] = 0.3
        self.ax2[0].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
        self.ax2[0].axis('equal') 
        #### Wake-Up-Time
        labels = []
        explode = []
        sizes = []
        this_sizes = {}
        for wake_up_time in wake_up_times:
            if wake_up_time not in this_sizes:
                this_sizes[wake_up_time] = 0
                labels.append(wake_up_time)
                explode.append(0)
            this_sizes[wake_up_time] += 1
        for wake_up_time in this_sizes:
            percent:float = (100/len(wake_up_times))*this_sizes[wake_up_time]
            sizes.append(percent)
        explode[sizes.index(max(sizes))] = 0.3
        self.ax2[1].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
        self.ax2[1].axis('equal') 

    def build_sleep_duration_days(self,data:dict,sleep_goal) -> tuple((list,float,list[str])):
        ### Sleep duration - Days (in hours)
        sleep_durations:list = []
        bad_sleep_durations:list = []
        good_sleep_durations:list = []
        average_sleep_dur:float = 0
        for day in data:
            in_hours:float = data[day]['sleep_duration']
            sleep_durations.append(in_hours)
            average_sleep_dur += in_hours
        average_sleep_dur:float = average_sleep_dur/len(data)
        average_sleep_dur_y = [average_sleep_dur for day in data]
        if isinstance(sleep_goal,bool) == False:
            for day in data:
                in_hours:float = data[day]['sleep_duration']
                if in_hours >= average_sleep_dur:
                    good_sleep_durations.append(in_hours)
                    bad_sleep_durations.append(0)
                else:
                    bad_sleep_durations.append(in_hours)
                    good_sleep_durations.append(0)
        days:list[str] = []
        if len(data.keys()) < 70:
            for day in data.keys():
                args:list = day.split("-")
                days.append(args[0]+"."+args[1]+".")
            x_ticks = 1
        else:
            x = 1
            for day in data.keys():
                days.append(str(x))
                x += 1
            x_ticks = 5
        self.ax3.plot(days,sleep_durations,label="Sleep duration in hours",color="black",linewidth=1.5,
            linestyle="-")
        self.ax3.plot(days,average_sleep_dur_y,label="Average sleep duration in hours",color="green",
            linestyle = "-.", linewidth = 2
        )
        if isinstance(sleep_goal,bool) == False:
            self.ax3.fill_between(days, bad_sleep_durations, alpha=0.3,color="red")
            self.ax3.fill_between(days, good_sleep_durations, alpha=0.3,color="seagreen")
        self.ax3.grid(True)
        self.ax3.set_xlabel("Days")
        self.ax3.set_ylabel("Sleep duration in hours")
        self.ax3.legend(loc='best')
        self.ax3.set_yticks(np.arange(0, max(sleep_durations)+2, 0.5))
        self.ax3.set_xticks(np.arange(0, len(days), x_ticks))
        return (sleep_durations,average_sleep_dur,days)

    def adjust_hours_and_minutes(self,time:str) -> tuple((int,int)):
        args:list = time.split(":")
        hours:int = int(args[0])
        minutes:int = int(args[1])
        if minutes > 0 and minutes < 15 and minutes > 10:
            minutes = 15
        if minutes > 0 and minutes <= 10:
            minutes = 0
        if minutes > 15 and minutes <= 20:
            minutes = 15
        if minutes > 20 and minutes < 30:
            minutes = 30
        if minutes > 30 and minutes < 45 and minutes <= 35:
            minutes = 30
        if minutes > 35 and minutes < 45:
            minutes = 45
        if minutes > 45 and minutes <= 50:
            minutes = 45
        if minutes > 50 and minutes > 50:
            minutes = 0
            if hours == 23:
                hours = 0
            else:
                hours += 1
        return (hours,minutes)

    def build_weekly_wake_up_mood_bar_graph(self,data:dict) -> None:
        ### Weekly wake-up-mood
        wake_up_moods:dict = {'weeks':[], 'good':[], 'bad':[], 'perfect':[]}
        day_counter:int = 1
        week_counter:int = 1
        for day in data: # idea with 'enumerate()'
            wake_up_mood:str = data[day]['wake_up_mood'].lower()
            this_week = f"Week {week_counter}"
            if this_week not in wake_up_moods['weeks']:
                wake_up_moods['weeks'].append(this_week)
                for mood in wake_up_moods:
                    if mood != "weeks":
                        if wake_up_mood != mood:
                            wake_up_moods[mood].append(0)
                        else:
                            wake_up_moods[mood].append(1)
            else:
                wake_up_moods[wake_up_mood][wake_up_moods['weeks'].index(this_week)] += 1
            if day_counter == 7:
                day_counter = 0
                week_counter += 1
            else:
                day_counter += 1
        width = 0.35
        weeks:list[str] = wake_up_moods['weeks']
        p = np.array(wake_up_moods['perfect'])
        g = np.array(wake_up_moods['good'])
        b = np.array(wake_up_moods['bad'])
        bar1 = self.ax[1][0].bar(weeks,p,width, color='limegreen', align='center',
            edgecolor='white', label="Perfect mood")
        bar2 = self.ax[1][0].bar(weeks,g,width, color='orange', edgecolor='white', align='center',
            label="Good mood", bottom = p)
        bar3 = self.ax[1][0].bar(weeks,b,width, color='red', align='center',
            label="Bad mood", bottom = p+g, edgecolor='white')
        self.ax[1][0].legend(loc='best')
        self.ax[1][0].set_title("Wake up mood (Weeks)")
        for r1, r2, r3 in zip(bar1,bar2,bar3):
            h1 = r1.get_height()
            h2 = r2.get_height()
            h3 = r3.get_height()
            self.ax[1][0].text(r1.get_x() + r1.get_width() / 2., h1 / 2., "%d" % h1, ha="center", 
                va="center", color="white", fontsize=13, fontweight="bold")
            self.ax[1][0].text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., "%d" % h2, ha="center", 
                va="center", color="white", fontsize=13, fontweight="bold")
            self.ax[1][0].text(r3.get_x() + r3.get_width() / 2., h1 + h2 + h3 / 2., "%d" % h3, ha="center", 
                va="center", color="white", fontsize=13, fontweight="bold")

    def build_monthly_wake_up_mood_bar_graph(self,data:dict) -> None:
        ### Monthly wake-up-mood
        wake_up_moods:dict = {'months':[], 'good':[], 'bad':[], 'perfect':[]}
        for day in data: # idea with 'enumerate()'
            month:str = int(day.split("-")[1])
            wake_up_mood:str = data[day]['wake_up_mood'].lower()
            if month not in wake_up_moods['months']:
                wake_up_moods['months'].append(month)
                for mood in wake_up_moods:
                    if mood != "months" and mood != wake_up_mood:
                        wake_up_moods[mood].append(0)
                    elif mood == wake_up_mood:
                        wake_up_moods[mood].append(1)
            else:
                wake_up_moods[wake_up_mood][wake_up_moods['months'].index(month)] += 1
        width = 0.35
        months = [self.month_names[month-1] for month in wake_up_moods['months']]
        p = np.array(wake_up_moods['perfect'])
        g = np.array(wake_up_moods['good'])
        b = np.array(wake_up_moods['bad'])
        bar1 = self.ax[1][0].bar(months,p,width, color='limegreen', align='center',
            edgecolor='white', label="Perfect mood")
        bar2 = self.ax[1][0].bar(months,g,width, color='orange', edgecolor='white', align='center',
            label="Good mood", bottom = p)
        bar3 = self.ax[1][0].bar(months,b,width, color='red', align='center',
            label="Bad mood", bottom = p+g, edgecolor='white')
        self.ax[1][0].legend(loc='best')
        self.ax[1][0].set_title("Wake up mood (Months)")
        for r1, r2, r3 in zip(bar1,bar2,bar3):
            h1 = r1.get_height()
            h2 = r2.get_height()
            h3 = r3.get_height()
            self.ax[1][0].text(r1.get_x() + r1.get_width() / 2., h1 / 2., "%d" % h1, ha="center", 
                va="center", color="white", fontsize=13, fontweight="bold")
            self.ax[1][0].text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., "%d" % h2, ha="center", 
                va="center", color="white", fontsize=13, fontweight="bold")
            self.ax[1][0].text(r3.get_x() + r3.get_width() / 2., h1 + h2 + h3 / 2., "%d" % h3, ha="center", 
                va="center", color="white", fontsize=13, fontweight="bold")

    def build_monthly_average_sleep_duration(self,data:dict) -> None:
        ### Average sleep duration - of every month (in hours)
        graph_data:dict = {}
        months:list[str] = []
        average_sleep_durations:list[float] = []
        for day in data:
            month:str = day.split("-")[1]
            if month not in graph_data.keys():
                graph_data[month] = []
            graph_data[month].append(data[day]['sleep_duration'])
        months = graph_data.keys()
        for month in graph_data:
            average_dur:float = 0
            for t in graph_data[month]:
                average_dur += t
            average_sleep_durations.append(average_dur/len(graph_data[month]))
        months = [self.month_names[int(month)-1] for month in months]
        self.ax[0][1].plot(months,average_sleep_durations,linewidth = 1.5,color="royalblue",linestyle = "-",
            label = "Average sleep duration (in hours) per month",marker = "o"
        )
        self.ax[0][1].fill_between(months, average_sleep_durations, alpha=0.3,color="royalblue")
        self.ax[0][1].set_title("Average sleep duration (in hours) per month")
        self.ax[0][1].legend(loc='best')
        self.ax[0][1].grid(True)
        self.ax[0][1].set_xticks(np.arange(0, len(months), 1))
        self.ax[0][1].set_yticks(np.arange(0, max(average_sleep_durations)+0.5, 0.5))

    def get_all_notes(self,data:dict) -> list[str]:
        all_notes:list[str] = []
        for date in data:
            notes:list = data[date]['notes'].split(self.note_seperator)
            for note in notes:
                note:str = note.strip().lower()
                if note not in all_notes and note != "" and note != " ":
                    all_notes.append(note)
        return all_notes

    def build_monthly_notes_graph(self,data:dict) -> None:
        ### Notes before bedtime (months)
        (months,years) = self.get_months_and_years(days = data) # years are here unnecessary
        all_notes:list[str] = self.get_all_notes(data = data)
        note_dict:dict = {}
        if len(all_notes) > 0:
            for note in all_notes:
                note_dict[note] = [0 for i in range(0,len(months))]
            for date in data:
                month:int = int(date.split('-')[1])
                day_notes:list[str] = data[date]['notes'].split(self.note_seperator)
                for note in day_notes:
                    note = note.strip().lower()
                    if note != "" and note != '' and note != ' ':
                        note_dict[note][months.index(month)] += 1
            months = [self.month_names[month-1] for month in months]
            self.ax[0][0].stackplot(months,note_dict.values(),labels = all_notes, alpha = 0.8)
            self.ax[0][0].legend(loc = "best")
            self.ax[0][0].set_xlabel("Months")
            self.ax[0][0].set_ylabel("Quantities")
            self.ax[0][0].grid(color = 'gray', alpha = 0.9, linestyle = '--', linewidth = 0.6)
            self.ax[0][0].set_title("Notes before bedtime (months)")
            tree = Tree("Notes Overview")
            for month in months:
                mo = tree.add(f"[yellow]{month}")
                for note in note_dict:
                    no = mo.add(f"[green]{note}")
                    no.add(f"[cyan]{str(note_dict[note][months.index(month)])}")
            pr(tree), print("\n")
        else:
            self.console.log(f"[red]There're no notes!")

    def build_monthly_wet_bed_graph(self,data:dict) -> None:
        ### Number of wet beds (months)
        (months,years) = self.get_months_and_years(days = data) # years are here unnecessary
        numbers:list[int] = [0 for i in range(0,len(months))]
        average_number:int = 0
        for day in data:
            month:str = int(day.split("-")[1])
            if "yes" in data[day]['wet_bed'].strip().lower():
                numbers[months.index(month)] += 1
        for number in numbers: average_number += number
        average_number = (average_number/len(numbers))
        average_numbers:list[int] = [average_number for i in range(0,len(numbers))]
        months = [self.month_names[month-1] for month in months]
        self.ax[1][1].plot(months,numbers,linewidth = 1,color="purple",linestyle="-",
            label="Number of wet beds per month", marker="x")
        self.ax[1][1].plot(months,average_numbers,linewidth = 1.5, color="seagreen",linestyle="-.",
            label=f"Average number of wet beds ({average_number})"
        )
        self.ax[1][1].legend(loc = "best")
        self.ax[1][1].grid(True)
        self.ax[1][1].set_xlabel("Months")
        self.ax[1][1].set_ylabel("Numbers")
        self.ax[1][1].set_yticks(np.arange(0, max(numbers)+1, 1))
        self.ax[1][1].set_title("Number of wet beds (months)")

    def show_year(self) -> None:
        year:str = self.console.input(f"[yellow]Enter year>[purple] ")
        sleep_goal:str = self.console.input(f"[yellow]Enter sleep goal - in hours (0 if not)>[purple] ")
        wet_bed_graph_state:str = self.console.input(f"[yellow]Show 'wet-bed' graph? (YES or NO) - default: [cyan]YES[yellow]>[purple] ")
        if sleep_goal == "0":
            sleep_goal = False
        else:
            try:
                sleep_goal:float = float(sleep_goal)
            except ValueError as error:
                sleep_goal = False
        try:
            year = int(year)
            year_data:dict = {}
            rows = self.db.get_all_entries()
            if len(rows) > 0:
                for row in rows:
                    row_year = row[0].split("-")[2]
                    if int(row_year) == year:
                        args:list = row[6].split(":")
                        hours:int = int(args[0])
                        minutes:int = int(args[1])
                        this_sleep_duration:float = float(f"{hours}.{(int((minutes/60)*100))}")
                        year_data[row[0]] = {
                            'bedtime': row[1],
                            'wake_up_time': row[2],
                            'wake_up_mood': row[3],
                            'wet_bed': row[4],
                            'notes': row[5],
                            'sleep_duration': this_sleep_duration
                        }
                if len(year_data) > 0:
                    wet_bed_graph_state:str = wet_bed_graph_state.strip().lower()
                    self.create_figures()
                    self.build_monthly_average_sleep_duration(data = year_data) # fig1
                    self.build_monthly_wake_up_mood_bar_graph(data = year_data) # fig1
                    self.build_monthly_notes_graph(data = year_data) # fig1
                    if wet_bed_graph_state != "no":
                        self.build_monthly_wet_bed_graph(data = year_data) # fig1
                    self.build_bedtime_and_wake_up_time_pies(data = year_data) # fig2
                    (sleep_durations,average_sleep_dur,days) = self.build_sleep_duration_days(data = year_data, 
                        sleep_goal = sleep_goal) # fig3
                    ### END
                    table = Table(title=f"Sleep-Doku ~ Overview - Year {year}")
                    table.add_column("Description", justify="left", style="blue", no_wrap=True)
                    table.add_column("Information", style="green")
                    table.add_row("Maximum sleep-duration",f"{max(sleep_durations)} hours")
                    table.add_row("Average sleep-duration",f"{average_sleep_dur} hours")
                    table.add_row("Number of entries",f"{len(days)} days")
                    self.console.print(table)
                    plt.show()
                else:
                    self.console.log(f"[red]There're no entries in the year '{year}'!")
            else:
                self.console.log(f"[red]There're no entries at all!")
        except Exception as error:
            self.console.log(f"[red]'{year}' is not a valid year!")
            self.console.log(f"[bold red]{str(error)}")

    def show_month(self) -> None:
        state:bool = True
        year:str = self.console.input(f"[yellow]Enter year>[purple] ")
        month:str = self.console.input(f"[yellow]Enter month (number)>[purple] ")
        if len(month) == 1:
            month = f"0{month}"
        sleep_goal:str = self.console.input(f"[yellow]Enter sleep goal - in hours (0 if not)>[purple] ")
        wet_bed_graph_state:str = self.console.input(f"[yellow]Show 'wet-bed' graph? (YES or NO) - default: [cyan]YES[yellow]>[purple] ")
        if sleep_goal == "0":
            sleep_goal = False
        else:
            try:
                sleep_goal:float = float(sleep_goal)
            except ValueError as error:
                sleep_goal = False
        try:
            month:int = int(month)
            year:int = int(year)
        except ValueError as error:
            state = False
        if state == True:
            year = int(year)
            data:dict = {}
            rows = self.db.get_all_entries()
            if len(rows) > 0:
                for row in rows:
                    args = row[0].split("-")
                    row_year = args[2]
                    row_month = args[1]
                    if int(row_year) == year and int(row_month) == month:
                        args:list = row[6].split(":")
                        hours:int = int(args[0])
                        minutes:int = int(args[1])
                        this_sleep_duration:float = float(f"{hours}.{(int((minutes/60)*100))}")
                        data[row[0]] = {
                            'bedtime': row[1],
                            'wake_up_time': row[2],
                            'wake_up_mood': row[3],
                            'wet_bed': row[4],
                            'notes': row[5],
                            'sleep_duration': this_sleep_duration
                        }
                if len(data) > 0:
                    wet_bed_graph_state:str = wet_bed_graph_state.strip().lower()
                    args:list[str] = list(data.keys())[0].split("-")
                    month_and_year:str = "-"+args[1]+"-"+args[2]
                    sorted_dates:list[str] = sorted([date.split("-")[0] for date in data.keys()])
                    sorted_data:dict = {}
                    for date in sorted_dates:
                        if len(date) == 1:
                            date = f"0{date}"
                        date:str = date+month_and_year
                        sorted_data[date] = data[date]
                    data = sorted_data
                    self.create_figures()
                    self.build_weekly_wake_up_mood_bar_graph(data = data) # fig1
                    self.build_bedtime_and_wake_up_time_pies(data = data) # fig2
                    (sleep_durations,average_sleep_dur,days) = self.build_sleep_duration_days(data = data, 
                        sleep_goal = sleep_goal) # fig3
                    ### END
                    table = Table(title=f"Sleep-Doku ~ Overview - Year {year}")
                    table.add_column("Description", justify="left", style="blue", no_wrap=True)
                    table.add_column("Information", style="green")
                    table.add_row("Maximum sleep-duration",f"{max(sleep_durations)} hours")
                    table.add_row("Average sleep-duration",f"{average_sleep_dur} hours")
                    table.add_row("Number of entries",f"{len(days)} days")
                    self.console.print(table)
                    plt.show()
                else:
                    self.console.log(f"[yellow]There're no entries of the month '{month}' in year '{year}'!")
            else:
                self.console.log(f"[red]There're no entries at all!")
        else:
            self.console.log(f"[red]The month '{month}' or the year '{year}' is not valid!")