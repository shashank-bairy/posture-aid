from PIL import Image, ImageTk
import cv2

def check_head_within_boundary(correct_pos, current_pos, pad_x=30, pad_y=30):
    (x1, y1, w1, h1) = correct_pos
    (x2, y2, w2, h2) = current_pos

    return (x1-pad_x <= x2 <= x2+w2 <= x1+w1+pad_x) and (y1-pad_y <= y2 <= y2+h2 <= y1+h1+pad_y)

def draw_boxes(img, correct_pos, current_pos, pad_x, pad_y):
    (fx, fy, fw, fh) = correct_pos
    (x, y, w, h) = current_pos
    frame = cv2.rectangle(
        img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    frame = cv2.rectangle(frame, (fx-pad_x, fy-pad_y),
                            (fx+fw+pad_x, fy+fh+pad_y), (0, 0, 255), 2)
    frame = cv2.flip(frame, 1)

    # convert colors from BGR to RGBA
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    current_image = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=current_image)

    return imgtk