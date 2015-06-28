import tornado.web
from ..db.user import current_user
from ..db.expansion import Expansion
from ..db.game import Game

import re

class GameHandler(tornado.web.RequestHandler):
  def _create(self, user, errors=False):
    self.render('game_create.html', handler=self, title='Create Game', user=user, errors=errors, expansions=Expansion.list_all())
  def _game(self, game, user):
    self.render('game.html', handler=self, title='Playing pyCAH', game=game, user=user)
  def _spectate(self, game, user):
    self.render('game_spectate.html', handler=self, title='Spectating pyCAH', game=game, user=user)
  def get(self, page):
    user = current_user(self)
    if not user:
      self.redirect('/')
    else:
      if page == '':
        self._create(user)
      else:
        gid = re.search(r'^\/(\d+)((?:\/spectate)?)$', page)
        if gid is None:
          self.redirect('/')
        else:
          game = Game.from_gid(gid.group(1))
          if game is None:
            self.redirect('/')
          elif gid.group(2) != '':
            self._spectate(game, user)
          else:
            self._game(game, user)

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
          self._create(user ,errors)
        else:
          game = Game.create(user, points_to_win, chosen_expansions)
          self.redirect('/game/{}'.format(game.gid))
      else:
        gid = re.search(r'^\/(\d+)$', page)
        if gid is None:
          self.redirect('/')
        else:
          game = Game.from_gid(gid.group(1))
          if game is None:
            self.redirect('/')
          else:
            do = self.get_argument('do')
            if do == 'Join':
              game.add_player(user)
              self.redirect('/game/{}'.format(game.gid))
            else:
              self.redirect('/game/{}/spectate'.format(game.gid))
