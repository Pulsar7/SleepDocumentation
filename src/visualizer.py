"""
@Name: Sleepdoku - Visualization
@Author: Benedikt Fichtner
@2022 (gregorianischer Kalender)/Version 2.0/Visualizer
"""
import sys,numpy as np
import matplotlib.pyplot as plt
from rich.table import Table

class VISUALIZE():
    def __init__(self,console,db,tables) -> None:
        (self.console,self.db, self.tables) = (console,db,tables)


    def create_figures(self) -> None:
        (fig, ax) = plt.subplots(2, 2, constrained_layout=True)
        (fig2,ax2) = plt.subplots(1, 2, constrained_layout=True)
        (fig3,ax3) = plt.subplots(1, 1, constrained_layout=True)
        fig.suptitle("")
        fig2.suptitle("Bedtime & Wake-Up-Time (hours:minutes)")
        fig3.suptitle("Sleep duration of each day (in hours)")
        fig.set_figwidth(13)
        fig.set_figheight(7)
        fig2.set_figwidth(13)
        fig2.set_figheight(7)
        fig3.set_figwidth(13)
        fig3.set_figheight(7)
        (self.fig,self.fig2,self.fig3,self.ax,self.ax2,self.ax3) = (fig,fig2,fig3,ax,ax2,ax3)

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
        self.ax3.legend()
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

    def build_month_average_sleep_duration(self,data:dict) -> None:
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
        self.ax[0][1].plot(months,average_sleep_durations,linewidth = 1.5,color="royalblue",linestyle = "-",
            label = "Average sleep duration (in hours) per month",marker = "o"
        )
        self.ax[0][1].fill_between(months, average_sleep_durations, alpha=0.3,color="royalblue")
        self.ax[0][1].set_title("Average sleep duration (in hours) per month")
        self.ax[0][1].legend()
        self.ax[0][1].grid(True)
        self.ax[0][1].set_xticks(np.arange(0, len(months), 1))
        self.ax[0][1].set_yticks(np.arange(0, max(average_sleep_durations), 0.5))

    

    def show_year(self) -> None:
        year:str = self.console.input(f"[yellow]Enter year>[purple] ")
        sleep_goal:str = self.console.input(f"[yellow]Enter goal goal - in hours (0 if not)>[purple] ")
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
                    self.create_figures()
                    self.build_month_average_sleep_duration(data = year_data) # fig1
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
        sleep_goal:str = self.console.input(f"[yellow]Enter sleep goal - in hours (0 if not)>[purple] ")
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
                    self.create_figures()
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