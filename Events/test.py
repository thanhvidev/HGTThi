                if quest_done2 == 0:
                    if is_casino_completed and is_giaitri_completed and is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done2 = 8 WHERE user_id = ?",   
                                        (balance_reward2, event_reward + 1, user_id))  
                        conn.commit()
                    elif is_casino_completed and is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 5 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0) + quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.commit()
                    elif is_casino_completed and is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 6 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0) + quest_dict.get('pray_xu', 0),  user_id))  
                        conn.commit()
                    elif is_giaitri_completed and is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 7 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0) + quest_dict.get('pray_xu', 0), user_id))  
                        conn.commit()
                    elif is_casino_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 1 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0), user_id))  
                        conn.commit()
                    elif is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 2 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.commit()
                    elif is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 3 WHERE user_id = ?",   
                                        (quest_dict.get('pray_xu', 0), user_id))  
                        conn.commit()

                # Kiểm tra nếu quest_done2 == 1 (đã hoàn thành nhiệm vụ time)
                elif quest_done2 == 1:
                    if is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 5 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.commit()
                    elif is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 6 WHERE user_id = ?",   
                                        (quest_dict.get('pray_xu', 0), user_id))  
                        conn.commit()

                # Kiểm tra nếu quest_done2 == 2 (đã hoàn thành nhiệm vụ message)
                elif quest_done2 == 2:
                    if is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 7 WHERE user_id = ?",   
                                        (quest_dict.get('pray_xu', 0), user_id))  
                        conn.commit()
                    elif is_casino_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 5 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0), user_id))  
                        conn.commit()

                # Kiểm tra nếu quest_done2 == 3 (đã hoàn thành nhiệm vụ image)
                elif quest_done2 == 3:
                    if is_casino_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 6 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0), user_id))  
                        conn.commit()
                    elif is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 7 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.commit()
        
                # Kiểm tra nếu tất cả các điều kiện hoàn thành và quest_done2 < 7
                if is_casino_completed and is_giaitri_completed and is_pray_completed and quest_done2 < 8:
                    if quest_done2 == 5:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + 1, quest_done2 = 8 WHERE user_id = ?", (user_id,))  
                        conn.commit()
                    elif quest_done2 == 6:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + 1, quest_done2 = 8 WHERE user_id = ?", (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.commit()
                    elif quest_done2 == 7:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + 1, quest_done2 = 8 WHERE user_id = ?", (quest_dict.get('casino_xu', 0), user_id))  
                        conn.commit()