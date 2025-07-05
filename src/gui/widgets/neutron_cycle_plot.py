"""
Neutron Cycle Visualization Widget

This widget displays the 6-factor neutron life cycle diagram.
"""
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QTransform, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF

class NeutronCyclePlot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(700, 600)
        self.data = None

    def update_data(self, data):
        """Update the plot with new data from the model."""
        self.data = data
        self.update()

    def paintEvent(self, event):
        """Draw the neutron cycle diagram."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        if not self.data:
            return

        self._draw_diagram(painter)

    def _draw_diagram(self, painter):
        box_width, box_height = 140, 60
        margin = 50

        center_x = self.width() / 2
        center_y = self.height() / 2
        
        radius_x = (self.width() - box_width - 2 * margin) / 2
        radius_y = (self.height() - box_height - 2 * margin) / 2
        
        num_boxes = 6
        
        box_defs = [
            {'key': 'start', 'title': 'Fast Neutrons (Gen N)'},
            {'key': 'after_P_AFR', 'title': 'After Fast Stage'},
            {'key': 'after_p', 'title': 'After Resonance Escape'},
            {'key': 'after_P_AFT', 'title': 'Thermal Neutrons'},
            {'key': 'after_f', 'title': 'Absorbed in Fuel'},
            {'key': 'final', 'title': 'Fast Neutrons (Gen N+1)'},
        ]
        
        positions = {}
        for i, box_def in enumerate(box_defs):
            angle = (math.pi / 2) - (i * 2 * math.pi / num_boxes)
            x = center_x + radius_x * math.cos(angle)
            y = center_y - radius_y * math.sin(angle)
            positions[box_def['key']] = QRectF(x - box_width / 2, y - box_height / 2, box_width, box_height)

        pops = self.data.get("populations", {})
        factors = self.data.get("factors", {})

        for box_def in box_defs:
            pop_value = pops.get(box_def['key'], 0)
            self._draw_box(painter, positions[box_def['key']], box_def['title'], f"{pop_value:.0f}")

        factor_mult = factors.get('epsilon', 1) * factors.get('P_AFR', 1)
        self._draw_arrow_and_factor(painter, positions['start'], positions['after_P_AFR'], f"ε × P_AFR ≈ {factor_mult:.4f}")
        self._draw_arrow_and_factor(painter, positions['after_P_AFR'], positions['after_p'], f"p ≈ {factors.get('p', 0):.4f}")
        self._draw_arrow_and_factor(painter, positions['after_p'], positions['after_P_AFT'], f"P_AFT ≈ {factors.get('P_AFT', 0):.4f}")
        self._draw_arrow_and_factor(painter, positions['after_P_AFT'], positions['after_f'], f"f ≈ {factors.get('f', 0):.4f}")
        self._draw_arrow_and_factor(painter, positions['after_f'], positions['final'], f"η ≈ {factors.get('eta', 0):.4f}")
        self._draw_arrow_and_factor(painter, positions['final'], positions['start'], "", is_feedback=True)

        painter.save()
        painter.setPen(QColor("#1E8449"))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        text_rect = QRectF(center_x - 100, center_y - 25, 200, 50)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"k_eff = {factors.get('k_eff', 0):.5f}")
        painter.restore()

    def _draw_box(self, painter, rect, title, value):
        painter.save()
        painter.setPen(QPen(QColor("#007BFF"), 2))
        painter.setBrush(QColor("#E7F3FF"))
        painter.drawRoundedRect(rect, 10, 10)
        
        painter.setPen(QColor("#333"))
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.drawText(rect.adjusted(5, 5, -5, -5), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, title)
        
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(rect.adjusted(5, 5, -5, -5), Qt.AlignmentFlag.AlignCenter, value)
        painter.restore()

    def _draw_arrow_and_factor(self, painter, start_rect, end_rect, text, is_feedback=False):
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
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            
            fm = painter.fontMetrics()
            text_rect = fm.boundingRect(text)
            mid_point = (p1 + p2) / 2
            
            offset_distance = 25
            perp_vec = QPointF(-line_vec.y(), line_vec.x()) / line_len * offset_distance
            
            text_rect.moveCenter((mid_point + perp_vec).toPoint())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

        pen = QPen(QColor("#555"), 2, Qt.PenStyle.SolidLine if not is_feedback else Qt.PenStyle.DashLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(p1, p2)

        angle = math.atan2(line_vec.y(), line_vec.x()) * 180.0 / math.pi
        
        transform = QTransform()
        transform.translate(p2.x(), p2.y())
        transform.rotate(angle)
        
        arrow_size = 10
        arrow_head = QPolygonF([
            QPointF(0, 0),
            QPointF(-arrow_size, -arrow_size / 2.0),
            QPointF(-arrow_size, arrow_size / 2.0),
        ])
        
        rotated_arrow_head = transform.map(arrow_head)
        painter.setBrush(QColor("#555"))
        painter.drawPolygon(rotated_arrow_head)
        
        painter.restore() 