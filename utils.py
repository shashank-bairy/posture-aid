def check_head_within_boundary(correct_pos, current_pos, pad=0):
    (x1, y1, w1, h1) = correct_pos
    (x2, y2, w2, h2) = current_pos

    return (x1-pad <= x2 <= x2+w2 <= x1+w1+pad) and (y1-pad <= y2 <= y2+h2 <= y1+h1+pad)
