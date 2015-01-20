import tornado.web
from ..db.user import current_user
from ..db.expansion import Expansion
from ..db.game import Game

import re

class GameHandler(tornado.web.RequestHandler):
  def _create(self, errors=False):
    self.render('game_create.html', handler=self, title='Create Game', errors=errors, expansions=Expansion.list_all())
  def _game(self, gid):
    self.render('game.html', handler=self, title='Playing pyCAH', gid=gid)
  def get(self, page):
    user = current_user(self)
    if not user:
      self.redirect('/')
    else:
      if page == '':
        self._create()
      else:
        gid = re.search(r'^\/(\d+)$', page)
        if gid is None:
          self.redirect('/')
        else:
          self._game(int(gid.group(1)))
  def post(self, page):
    user = current_user(self)
    if not user:
      self.redirect('/')
    else:
      if page == '':
        errors = []
        points_to_win = 6
        try:
          points_to_win = int(self.get_argument('points'))
        except ValueError:
          errors.append('Invalid number for points to win.')
        if not (2 <= points_to_win <= 32):
          errors.append('Points to win must be between 2 and 32 inclusive.')
        chosen_expansions = []
        expansions = self.get_arguments('expansion')
        for eid in expansions:
          expansion = Expansion.from_eid(int(eid))
          if not expansion:
            errors.append('Invalid expansion selected.')
            break
          else:
            chosen_expansions.append(expansion)
        if len(expansions) == 0:
          errors.append('You have not selected any expansions.')
        elif sum([e.num_white for e in chosen_expansions]) < 100:
          errors.append('You have not selected sufficient white cards.')
        if len(errors) > 0:
          self._create(errors)
        else:
          game = Game.create(points_to_win, user, chosen_expansions)
          self.redirect('/game/{}'.format(game.gid))
      else:
        raise NotImplemented
