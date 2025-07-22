import tkinter as tk
from tkinter import filedialog, messagebox
from data_loader import load_staffs_from_excel, save_shift_to_excel
from scheduler import assign_shifts
from ai_suggester import suggest_replacement

class ShiftApp:
    def __init__(self, root):
        self.root = root
        self.root.title("シフト管理ツール")
        self.staffs = []
        self.shift_table = None
        self.config = {
            "DAYS": [1,2,3,4,5,6,7],
            "HOURS": list(range(8,21)),
            "BUSY_HOURS": set([11,12,13,17,18,19]),
            "BUSY_NUM": 4,
            "NORMAL_NUM": 3,
            "LEADER_NEEDED": 1
        }

        tk.Button(root, text="Excel読込", command=self.load_excel).pack()
        tk.Button(root, text="自動割当", command=self.assign_shifts).pack()
        tk.Button(root, text="Excel保存", command=self.save_excel).pack()
        self.info = tk.Label(root, text="")
        self.info.pack()
        self.listbox = tk.Listbox(root, width=80)
        self.listbox.pack()

        # 欠勤者選択
        tk.Label(root, text="欠勤スタッフ名:").pack()
        self.absent_entry = tk.Entry(root)
        self.absent_entry.pack()
        tk.Button(root, text="穴埋め候補表示", command=self.show_replacement).pack()
        self.candidate_label = tk.Label(root, text="")
        self.candidate_label.pack()

    def load_excel(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.staffs = load_staffs_from_excel(file_path)
            self.info.config(text=f"{len(self.staffs)}人のスタッフ情報を読み込みました")
        else:
            self.info.config(text="ファイルが選択されませんでした")

    def assign_shifts(self):
        if not self.staffs:
            self.info.config(text="スタッフ情報を読み込んでください")
            return
        slots = assign_shifts(self.staffs, self.config)
        self.shift_table = slots  # slotsはリスト
        self.listbox.delete(0, tk.END)
        for slot in self.shift_table:
            assigned = ",".join(slot["assigned"])
            self.listbox.insert(tk.END, f"{slot['day']}日 {slot['hour']}時: {assigned}")

    def save_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if self.shift_table:
            save_shift_to_excel(self.shift_table, file_path)
            messagebox.showinfo("保存", "シフト表を保存しました")
        else:
            messagebox.showwarning("保存", "シフト表がありません")

    def show_replacement(self):
        absent_name = self.absent_entry.get()
        selected = self.listbox.curselection()
        if not selected or not self.shift_table:
            self.candidate_label.config(text="シフト枠を選んでください")
            return
        slot = self.shift_table[selected[0]]
        used_staffs = slot["assigned"]
        candidates = suggest_replacement(self.staffs, slot, used_staffs, absent_name)
        if not candidates:
            self.candidate_label.config(text="候補者なし")
        else:
            msg = "\n".join([f"{c['name']} ({c.get('reason','')})" for c in candidates])
            self.candidate_label.config(text=msg)

def main():
    root = tk.Tk()
    app = ShiftApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()