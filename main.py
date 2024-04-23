import tkinter as tk


def sort_vertices_clockwise(vertices):
    min_x, min_y = max_x, max_y = vertices[0][0], vertices[0][1]

    for x, y in vertices:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    sorted_vertices = [(min_x, min_y), (max_x, min_y),
                       (max_x, max_y), (min_x, max_y)]

    return sorted_vertices


def liang_barsky_clipper(start, end, window):
    x1, y1 = start[0], start[1]
    x2, y2 = end[0], end[1]

    p = [x1 - x2, x2 - x1, y1 - y2, y2 - y1]
    q = [x1 - window[0][0], window[1][0] - x1, y1 - window[0][1], window[2][1] - y1]
    t_min, t_max = 0, 1

    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None, None
        else:
            t = q[i] / p[i]
            if p[i] < 0 and t > t_min:
                t_min = t
            elif p[i] > 0 and t < t_max:
                t_max = t

    if t_min > t_max:
        return None, None

    return ((x1 + t_min * (x2 - x1), y1 + t_min * (y2 - y1)),
            (x1 + t_max * (x2 - x1), y1 + t_max * (y2 - y1)))


class ClippingWindow:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=800, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.segments = []
        self.clip_start_x = None
        self.clip_start_y = None
        self.clip_end_x = None
        self.clip_end_y = None
        self.drawing_clip = False

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(fill=tk.X, expand=False)

        self.segment_button = tk.Button(self.button_frame, text="Draw Segment", command=self.toggle_segment)
        self.segment_button.pack(side=tk.LEFT)

        self.clip_button = tk.Button(self.button_frame, text="Draw Clipping Window", command=self.toggle_clip)
        self.clip_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self.button_frame, text="Clear All", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def toggle_segment(self):
        self.clip_start_x = None
        self.clip_start_y = None
        self.clip_end_x = None
        self.clip_end_y = None
        self.drawing_clip = False

    def toggle_clip(self):
        self.clip_start_x = None
        self.clip_start_y = None
        self.clip_end_x = None
        self.clip_end_y = None
        self.drawing_clip = True

    def clear_canvas(self):
        self.canvas.delete("all")
        self.segments.clear()

    def on_click(self, event):
        if self.drawing_clip:
            self.clip_start_x = event.x
            self.clip_start_y = event.y
        else:
            if self.clip_start_x is None and self.clip_start_y is None:
                self.clip_start_x = event.x
                self.clip_start_y = event.y
            else:
                end_x = event.x
                end_y = event.y
                self.canvas.create_line(self.clip_start_x, self.clip_start_y, end_x, end_y, fill='black', width=2)
                self.segments.append(((self.clip_start_x, self.clip_start_y), (end_x, end_y)))
                self.clip_start_x = None
                self.clip_start_y = None

    def on_motion(self, event):
        if self.drawing_clip:
            if self.clip_start_x is not None and self.clip_start_y is not None:
                self.canvas.delete("current_clip")
                self.canvas.create_rectangle(self.clip_start_x, self.clip_start_y,
                                             event.x, event.y,
                                             outline='purple', width=2, tag="current_clip")

    def on_release(self, event):
        if self.drawing_clip:
            self.clip_end_x = event.x
            self.clip_end_y = event.y

            clip_window = [(self.clip_start_x, self.clip_start_y),
                           (self.clip_end_x, self.clip_start_y),
                           (self.clip_end_x, self.clip_end_y),
                           (self.clip_start_x, self.clip_end_y)]
            clip_window = sort_vertices_clockwise(clip_window)
            self.canvas.delete("clipped_segment")

            for segment in self.segments:
                clipped_segment = liang_barsky_clipper(segment[0], segment[1], clip_window)
                if clipped_segment[0] is not None and clipped_segment[1] is not None:
                    self.canvas.create_line(clipped_segment[0][0], clipped_segment[0][1],
                                            clipped_segment[1][0], clipped_segment[1][1],
                                            fill='red', width=3, tag="clipped_segment")


def main():
    root = tk.Tk()
    root.title("Liang–Barsky algorithm")
    ClippingWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
