from models import TrainingSession, User
from assistant.knowledge_base import CONCEPTS, FAQ, HINTS, FEEDBACK_RULES
from datetime import datetime


class ChatbotAssistant:
    def __init__(self):
        pass

    def get_welcome_message(self):
        return {
            "type": "menu",
            "text": "Hi! 👋 How can I help you today?",
            "options": [
                {"id": "1", "label": "📚 Learn Concepts", "action": "learn_menu"},
                {"id": "2", "label": "📊 Check My Progress", "action": "progress"},
                {"id": "3", "label": "💡 Get Help Now", "action": "help_menu"},
                {"id": "4", "label": "❓ FAQ", "action": "faq_menu"}
            ]
        }

    def get_learn_menu(self):
        return {
            "type": "menu",
            "text": "📚 What would you like to learn about?",
            "options": [
                {"id": f"learn_{key}", "label": f"{value['title']}", "action": "show_concept", "param": key}
                for key, value in CONCEPTS.items()
            ] + [
                {"id": "back", "label": "← Back", "action": "welcome"}
            ]
        }

    def get_concept(self, concept_key):
        if concept_key not in CONCEPTS:
            return {"type": "error", "text": "Concept not found"}
        
        concept = CONCEPTS[concept_key]
        text = f"""{concept['title']}

{concept.get('definition', '')}

📖 What is it?
{concept.get('what_is_it', '')}
"""
        
        if 'how_it_spreads' in concept:
            text += "\n🔄 How it spreads:\n"
            for item in concept['how_it_spreads'][:5]:
                text += f"• {item}\n"
        
        if 'how_it_works' in concept:
            text += "\n🔄 How it works:\n"
            for item in concept['how_it_works']:
                text += f"• {item}\n"
        
        if 'signs_of_infection' in concept:
            text += "\n⚠️ Signs of infection:\n"
            for item in concept['signs_of_infection']:
                text += f"• {item}\n"
        
        if 'red_flags' in concept:
            text += "\n🚩 Red flags:\n"
            for item in concept['red_flags'][:5]:
                text += f"• {item}\n"
        
        if 'how_to_protect' in concept:
            text += "\n🛡️ How to protect:\n"
            for item in concept['how_to_protect'][:5]:
                text += f"• {item}\n"
        
        if 'real_world_examples' in concept:
            text += "\n📰 Real-world examples:\n"
            for item in concept['real_world_examples'][:2]:
                text += f"• {item}\n"
        
        if 'related_scenarios' in concept:
            text += "\n🎮 Practice in:\n"
            for scenario in concept['related_scenarios']:
                text += f"→ {scenario}\n"
        
        return {
            "type": "info",
            "text": text,
            "options": [
                {"id": "back_learn", "label": "← Back", "action": "welcome"}
            ]
        }

    def get_progress(self, user_id):
        from scenario_manager import scenario_manager
        
        user = User.query.get(user_id)
        if not user:
            return {"type": "error", "text": "User not found"}
        
        sessions = TrainingSession.query.filter_by(user_id=user_id).all()
        completed = [s for s in sessions if s.status == 'completed']
        
        if not completed:
            text = """📊 YOUR PERFORMANCE

No completed scenarios yet. 
Start by choosing a scenario to try!

[Go to Scenarios] [← Back]"""
            return {
                "type": "info",
                "text": text,
                "options": [
                    {"id": "back", "label": "← Back", "action": "welcome"}
                ]
            }
        
        scores = [s.score for s in completed if s.score]
        avg_score = sum(scores) / len(scores) if scores else 0
        total_time = sum((s.time_taken or 0) for s in completed) // 60
        
        # Check if user has completed less than 5 scenarios
        if len(completed) < 5:
            scenarios_needed = 5 - len(completed)
            text = f"""📊 YOUR PERFORMANCE

📈 Current Stats:
✅ Scenarios Completed: {len(completed)}/5
📊 Average Score: {avg_score:.1f}%
⏱️ Total Time: {total_time} minutes

📌 DETAILED FEEDBACK:
Complete {scenarios_needed} more scenario(s) to unlock detailed metrics breakdown for each skill area!

🎯 RECOMMENDATION:
Keep practicing! Complete 5 scenarios for personalized feedback."""
        else:
            # Calculate metrics breakdown (detection, containment, eradication, recovery, communication)
            metrics = {
                'detection': 0,
                'containment': 0,
                'eradication': 0,
                'recovery': 0,
                'communication': 0
            }
            
            # Sum metrics from all completed sessions
            for session in completed:
                metrics['detection'] += session.detection_score or 0
                metrics['containment'] += session.containment_score or 0
                metrics['eradication'] += session.eradication_score or 0
                metrics['recovery'] += session.recovery_score or 0
                metrics['communication'] += session.communication_score or 0
            
            # Calculate percentage for each metric (0-100)
            # Assuming max 100 per metric per scenario
            total_scenarios = len(completed)
            max_possible_per_metric = 100 * total_scenarios
            
            metrics_pct = {
                'detection': int((metrics['detection'] / max_possible_per_metric * 100)) if max_possible_per_metric > 0 else 0,
                'containment': int((metrics['containment'] / max_possible_per_metric * 100)) if max_possible_per_metric > 0 else 0,
                'eradication': int((metrics['eradication'] / max_possible_per_metric * 100)) if max_possible_per_metric > 0 else 0,
                'recovery': int((metrics['recovery'] / max_possible_per_metric * 100)) if max_possible_per_metric > 0 else 0,
                'communication': int((metrics['communication'] / max_possible_per_metric * 100)) if max_possible_per_metric > 0 else 0
            }
            
            # Sort metrics from best to worst
            sorted_metrics = sorted(metrics_pct.items(), key=lambda x: x[1], reverse=True)
            
            # Build metrics display with emojis
            emoji_map = {
                'detection': '🔍',
                'containment': '🚫',
                'eradication': '🧹',
                'recovery': '♻️',
                'communication': '📢'
            }
            
            metrics_text = "\n".join([f"{emoji_map[metric]} {metric.capitalize()}: {pct}%" for metric, pct in sorted_metrics])
            
            text = f"""📊 YOUR PERFORMANCE

📈 Overall Stats:
✅ Scenarios Completed: {len(completed)}
📊 Average Score: {avg_score:.1f}%
⏱️ Total Time: {total_time} minutes

📊 SKILL BREAKDOWN (Best to Worst):
{metrics_text}

🎯 RECOMMENDATION:
Focus on improving your lower-performing skills!"""
        
        return {
            "type": "info",
            "text": text,
            "options": [
                {"id": "back", "label": "← Back", "action": "welcome"}
            ]
        }

    def get_help_menu(self):
        return {
            "type": "menu",
            "text": "💡 WHAT DO YOU NEED HELP WITH?",
            "options": [
                {"id": "help_concept", "label": "🔍 Explain this concept", "action": "learn_menu"},
                {"id": "help_faq", "label": "❓ General questions", "action": "faq_menu"},
                {"id": "back", "label": "← Back", "action": "welcome"}
            ]
        }

    def get_faq_menu(self):
        return {
            "type": "menu",
            "text": "❓ FREQUENTLY ASKED QUESTIONS",
            "options": [
                {"id": f"faq_{key}", "label": value['question'], "action": "show_faq", "param": key}
                for key, value in FAQ.items()
            ] + [
                {"id": "back", "label": "← Back", "action": "welcome"}
            ]
        }

    def get_faq_answer(self, faq_key):
        if faq_key not in FAQ:
            return {"type": "error", "text": "FAQ not found"}
        
        faq = FAQ[faq_key]
        text = f"""{faq['question']}

{faq['answer']}"""
        
        return {
            "type": "info",
            "text": text,
            "options": [
                {"id": "back_faq", "label": "← Back", "action": "welcome"}
            ]
        }

    def get_scenario_feedback(self, session_id):
        session = TrainingSession.query.get(session_id)
        if not session:
            return {"type": "error", "text": "Session not found"}
        
        score = session.score or 0
        time_taken = (session.time_taken or 0) // 60  # Convert seconds to minutes
        
        text = f"""✅ SCENARIO COMPLETE!

Score: {score}/100
Time: {time_taken} minutes
Status: {'Excellent!' if score >= 85 else 'Good!' if score >= 70 else 'Keep practicing!'}

"""
        
        if score >= 85:
            text += "💪 Great job! You're performing well.\n\n"
        elif score >= 70:
            text += "📈 Good effort! Room for improvement.\n\n"
        else:
            text += "🎯 Keep practicing - you'll improve!\n\n"
        
        text += """Review the detailed feedback to see:
✓ What you did well
✗ What could be better
💡 Tips for next time"""
        
        return {
            "type": "info",
            "text": text,
            "options": [
                {"id": "back", "label": "← Back", "action": "welcome"}
            ]
        }

    def handle_action(self, action, user_id=None, param=None):
        if action == "welcome":
            return self.get_welcome_message()
        elif action == "learn_menu":
            return self.get_learn_menu()
        elif action == "show_concept":
            return self.get_concept(param)
        elif action == "progress":
            return self.get_progress(user_id)
        elif action == "help_menu":
            return self.get_help_menu()
        elif action == "faq_menu":
            return self.get_faq_menu()
        elif action == "show_faq":
            return self.get_faq_answer(param)
        else:
            return self.get_welcome_message()


chatbot = ChatbotAssistant()
