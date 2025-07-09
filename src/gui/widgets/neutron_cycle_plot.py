"""
Neutron Cycle Visualization Widget

This widget displays the 6-factor neutron life cycle diagram.
"""
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QTransform, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF
from typing import Optional
from ..widgets.info_manager import InfoManager

class NeutronCyclePlot(QWidget):
    def __init__(self, parent=None, info_manager: Optional[InfoManager] = None):
        super().__init__(parent)
        self.setMinimumSize(900, 750)  # Increased minimum size to accommodate larger text
        self.data = None
        self.info_manager = info_manager
        self._box_positions = {}
        self._factor_info = {}
        self.setMouseTracking(True)

    def update_data(self, data):
        """Update the plot with new data from the model."""
        self.data = data
        self.update()

    def leaveEvent(self, event):
        """Clear info when mouse leaves the widget."""
        if self.info_manager:
            self.info_manager.info_cleared.emit()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        """Show information based on cursor position."""
        if not self.info_manager:
            super().mouseMoveEvent(event)
            return

        pos = event.position()

        # Check for hover over boxes
        for key, rect in self._box_positions.items():
            if rect.contains(pos):
                info = self._factor_info.get(f"box_{key}")
                if info:
                    self.info_manager.info_requested.emit(info)
                    return
        
        # Check for hover over arrows/factors
        for key, info in self._factor_info.items():
            if key.startswith("factor_") and info.get("rect") and info["rect"].contains(pos):
                self.info_manager.info_requested.emit(info["text"])
                return

        # If not over anything, clear
        self.info_manager.info_cleared.emit()
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        """Draw the neutron cycle diagram."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        if not self.data:
            return

        self._draw_diagram(painter)

    def _draw_diagram(self, painter):
        # Reset info from previous draws
        self._box_positions = {}
        self._factor_info = {}

        box_width, box_height = 200, 90  # Further increased box size
        margin = 70  # Increased margin

        center_x = self.width() / 2
        center_y = self.height() / 2
        
        radius_x = (self.width() - box_width - 2 * margin) / 2
        radius_y = (self.height() - box_height - 2 * margin) / 2
        
        num_boxes = 6
        
        box_defs = [
            {
                'key': 'start', 
                'title': 'Neutrons Rapides\n(Génération N)', 
                'desc': "Population de neutrons rapides issus de la fission de la génération précédente.\n\nCes neutrons ont une énergie élevée (environ 2 MeV) et doivent être ralentis pour devenir efficaces dans les réactions de fission thermique."
            },
            {
                'key': 'after_P_AFR', 
                'title': 'Après Étape Rapide\n(ε × P_AFR)', 
                'desc': "Neutrons rapides restants après la fission rapide et les fuites rapides.\n\nLa fission rapide (ε) augmente le nombre de neutrons, tandis que les fuites rapides (P_AFR) en font perdre une partie."
            },
            {
                'key': 'after_p', 
                'title': 'Après Échappement\naux Résonances (p)', 
                'desc': "Neutrons ayant échappé à la capture par résonance pendant leur ralentissement.\n\nLe facteur antitrappe (p) représente la probabilité d'éviter l'absorption par l'U-238 lors du ralentissement."
            },
            {
                'key': 'after_P_AFT', 
                'title': 'Neutrons Thermiques\n(P_AFT)', 
                'desc': "Neutrons devenus thermiques et n'ayant pas fui le réacteur.\n\nCes neutrons ont une énergie faible (0,025 eV) et sont très efficaces pour provoquer la fission de l'U-235."
            },
            {
                'key': 'after_f', 
                'title': 'Absorbés dans\nle Combustible (f)', 
                'desc': "Neutrons thermiques absorbés par le combustible (U-235, U-238, etc.).\n\nLe facteur d'utilisation thermique (f) dépend de la concentration en bore et de la position des barres de contrôle."
            },
            {
                'key': 'final', 
                'title': 'Nouveaux Neutrons\n(Génération N+1)', 
                'desc': "Nouveaux neutrons rapides produits par la fission thermique.\n\nLe facteur de reproduction (η) détermine combien de neutrons sont produits par neutron absorbé dans le combustible."
            },
        ]
        
        for i, box_def in enumerate(box_defs):
            angle = (math.pi / 2) - (i * 2 * math.pi / num_boxes)
            x = center_x + radius_x * math.cos(angle)
            y = center_y - radius_y * math.sin(angle)
            self._box_positions[box_def['key']] = QRectF(x - box_width / 2, y - box_height / 2, box_width, box_height)

        pops = self.data.get("populations", {})
        factors = self.data.get("factors", {})

        for box_def in box_defs:
            pop_value = pops.get(box_def['key'], 0)
            self._draw_box(painter, self._box_positions[box_def['key']], box_def['title'], f"{pop_value:.0f}")
            
            # Enhanced hover information
            enhanced_info = (
                f"{box_def['title'].replace(chr(10), ' ')}\n\n"
                f"Population actuelle : {pop_value:.0f} neutrons\n"
                f"Pourcentage du total initial : {(pop_value/pops.get('start', 1)*100):.1f}%\n\n"
                f"{box_def['desc']}"
            )
            self._factor_info[f"box_{box_def['key']}"] = enhanced_info

        # Enhanced factor descriptions
        factor_descriptions = {
            "epsilon_P_AFR": f"Facteur de fission rapide (ε = {factors.get('epsilon', 0):.4f}) et Probabilité de non-fuite rapide (P_AFR = {factors.get('P_AFR', 0):.4f})\n\nLa fission rapide augmente le nombre de neutrons grâce aux fissions induites par les neutrons rapides dans l'U-238. Les fuites rapides représentent les neutrons qui s'échappent du cœur avant d'être ralentis.",
            "p": f"Facteur antitrappe (p = {factors.get('p', 0):.4f})\n\nReprésente la probabilité qu'un neutron évite la capture par résonance dans l'U-238 pendant son ralentissement.\n\nCe facteur dépend de DEUX effets de température :\n• Température du combustible (effet Doppler) : élargit les résonances d'absorption\n• Température du modérateur : affecte la densité de l'eau et l'efficacité du ralentissement\n\nUne augmentation de l'une ou l'autre de ces températures diminue le facteur p.",
            "P_AFT": f"Probabilité de non-fuite thermique (P_AFT = {factors.get('P_AFT', 0):.4f})\n\nProbabilité qu'un neutron thermique ne s'échappe pas du cœur. Dépend de la géométrie du réacteur et de la section efficace d'absorption.",
            "f": f"Facteur d'utilisation thermique (f = {factors.get('f', 0):.4f})\n\nRapport des neutrons thermiques absorbés dans le combustible sur le total des neutrons thermiques absorbés. Diminue avec l'augmentation de la concentration en bore ou l'insertion des barres de contrôle.",
            "eta": f"Facteur de reproduction (η = {factors.get('eta', 0):.4f})\n\nNombre moyen de neutrons de fission produits par neutron thermique absorbé dans le combustible. Dépend de l'enrichissement en U-235 et du taux de combustion.",
            "feedback": "Cycle de vie du neutron\n\nCe diagramme montre le cycle complet d'une génération de neutrons. Pour maintenir la criticité (k_eff = 1), chaque génération doit produire exactement le même nombre de neutrons que la précédente."
        }

        factor_mult = factors.get('epsilon', 1) * factors.get('P_AFR', 1)
        self._draw_arrow_and_factor(painter, self._box_positions['start'], self._box_positions['after_P_AFR'], f"ε × P_AFR ≈ {factor_mult:.3f}", "epsilon_P_AFR", factor_descriptions["epsilon_P_AFR"])
        self._draw_arrow_and_factor(painter, self._box_positions['after_P_AFR'], self._box_positions['after_p'], f"p ≈ {factors.get('p', 0):.3f}", "p", factor_descriptions["p"])
        self._draw_arrow_and_factor(painter, self._box_positions['after_p'], self._box_positions['after_P_AFT'], f"P_AFT ≈ {factors.get('P_AFT', 0):.3f}", "P_AFT", factor_descriptions["P_AFT"])
        self._draw_arrow_and_factor(painter, self._box_positions['after_P_AFT'], self._box_positions['after_f'], f"f ≈ {factors.get('f', 0):.3f}", "f", factor_descriptions["f"])
        self._draw_arrow_and_factor(painter, self._box_positions['after_f'], self._box_positions['final'], f"η ≈ {factors.get('eta', 0):.3f}", "eta", factor_descriptions["eta"])
        self._draw_arrow_and_factor(painter, self._box_positions['final'], self._box_positions['start'], "", "feedback", factor_descriptions["feedback"], is_feedback=True)

        # Enhanced center text with more information
        painter.save()
        painter.setPen(QColor("#1E8449"))
        painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))  # Much larger font size
        k_eff = factors.get('k_eff', 0)
        
        # Main k_eff value
        main_text_rect = QRectF(center_x - 150, center_y - 50, 300, 40)
        painter.drawText(main_text_rect, Qt.AlignmentFlag.AlignCenter, f"k_eff = {k_eff:.2f}")
        
        # Status indicator
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Larger status text
        status_color = QColor("#1E8449")  # Green for critical
        status_text = "CRITIQUE"
        
        if k_eff > 1.001:
            status_color = QColor("#E74C3C")  # Red for supercritical
            status_text = "SURCRITIQUE"
        elif k_eff < 0.999:
            status_color = QColor("#F39C12")  # Orange for subcritical
            status_text = "SOUS-CRITIQUE"
            
        painter.setPen(status_color)
        status_rect = QRectF(center_x - 100, center_y - 5, 200, 25)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, status_text)
        
        # Add formula reminder
        painter.setPen(QColor("#7F8C8D"))
        painter.setFont(QFont("Arial", 12))  # Larger formula text
        formula_rect = QRectF(center_x - 140, center_y + 25, 280, 20)
        painter.drawText(formula_rect, Qt.AlignmentFlag.AlignCenter, "k∞ × P_NL = η × ε × p × f × P_AFR × P_AFT")
        
        painter.restore()

    def _draw_box(self, painter, rect, title, value):
        painter.save()
        painter.setPen(QPen(QColor("#007BFF"), 3))  # Thicker border
        painter.setBrush(QColor("#E7F3FF"))
        painter.drawRoundedRect(rect, 12, 12)  # Larger border radius
        
        painter.setPen(QColor("#333"))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # Much larger title font
        
        # Draw title with word wrapping
        title_rect = rect.adjusted(8, 8, -8, -35)  # More padding
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap, title)
        
        # Draw value
        painter.setFont(QFont("Arial", 18, QFont.Weight.Bold))  # Much larger value font
        value_rect = rect.adjusted(8, 35, -8, -8)  # More padding
        painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, value)
        painter.restore()

    def _draw_arrow_and_factor(self, painter, start_rect, end_rect, text, key, desc, is_feedback=False):
        start_point = start_rect.center()
        end_point = end_rect.center()

        line_vec = end_point - start_point
        line_len = (line_vec.x()**2 + line_vec.y()**2)**0.5
        if line_len == 0: return

        p1 = start_point + (line_vec / line_len) * (start_rect.width() / 2 * 0.9)
        p2 = end_point - (line_vec / line_len) * (end_rect.width() / 2 * 1.1)

        painter.save()
        
        if not is_feedback:
            painter.setPen(QColor("#D6336C"))
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # Much larger factor font
            
            fm = painter.fontMetrics()
            text_rect = QRectF(fm.boundingRect(text))
            mid_point = (p1 + p2) / 2
            
            offset_distance = 40  # Increased offset to prevent overlap
            perp_vec = QPointF(-line_vec.y(), line_vec.x()) / line_len * offset_distance
            
            text_rect.moveCenter(mid_point + perp_vec)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
            
            # Store info for hover with enhanced descriptions
            self._factor_info[f"factor_{key}"] = {"rect": text_rect.adjusted(-15, -15, 15, 15), "text": f"{desc}\n\nValeur actuelle : {text}"}

        pen = QPen(QColor("#555"), 4, Qt.PenStyle.SolidLine if not is_feedback else Qt.PenStyle.DashLine)  # Thicker lines
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(p1, p2)

        # Larger arrow heads
        angle = math.atan2(line_vec.y(), line_vec.x()) * 180.0 / math.pi
        
        transform = QTransform()
        transform.translate(p2.x(), p2.y())
        transform.rotate(angle)
        
        arrow_size = 16  # Much larger arrows
        arrow_head = QPolygonF([
            QPointF(0, 0),
            QPointF(-arrow_size, -arrow_size / 2.0),
            QPointF(-arrow_size, arrow_size / 2.0),
        ])
        
        rotated_arrow_head = transform.map(arrow_head)
        painter.setBrush(QColor("#555"))
        painter.drawPolygon(rotated_arrow_head)
        
        painter.restore() 